from common import TestID, load_common_properties
from eu.emi.security.authn.x509.impl import PEMCredential
from exceptions import Exception
from gov.lbl.srm.StorageResourceManager import TStatusCode
from jarray import array
from java.io import FileInputStream
from javax.net.ssl import X509ExtendedKeyManager
from net.grinder.plugin.http import HTTPRequest
from net.grinder.script import Test
from net.grinder.script.Grinder import grinder
from org.italiangrid.srm.client import SRMClient, SRMClientFactory
import ptg
import random
import sptg
import string
import time
import traceback
import uuid

## This loads the base properties inside grinder properties
## Should be left at the top of the script execution
load_common_properties()

error          = grinder.logger.error
info           = grinder.logger.info
debug          = grinder.logger.debug

props          = grinder.properties

PROXY_FILE     = props['client.proxy']
FE_HOST        = props['storm.host']
BASE_FILE_PATH = props['ptg-sync.base_file_path']

SRM_ENDPOINT   = "https://%s" % FE_HOST
SURL_PREFIX    = "srm://%s/%s" % (FE_HOST, BASE_FILE_PATH)

WAITING_STATES = [TStatusCode.SRM_REQUEST_QUEUED, TStatusCode.SRM_REQUEST_INPROGRESS]

SRM_SUCCESS  = TStatusCode.SRM_SUCCESS

# Start sleeping between sptg requests after this number
SLEEP_THRESHOLD = int(props['ptg-sync.sleep_threshold'])

## Sleep time (seconds)
SLEEP_TIME = float(props['ptg-sync.sleep_time'])

## Perform an srmPing before running the test to
## rule out the handshake time from the stats
DO_HANDSHAKE = bool(props['ptg-sync.do_handshake'])

## Number of files created in the ptg directory
NUM_FILES = 50

def status_code(resp):
    return resp.returnStatus.statusCode

def explanation(resp):
    return resp.returnStatus.explanation

def compute_surls(base_dir):
    random_index = random.randint(1, NUM_FILES)
    surl = "%s/f%d" % (base_dir, random_index)
    return [surl]

def check_success(res, msg):
    if status_code(res) != SRM_SUCCESS:
        error_msg = "%s. %s (expl: %s)" % (msg, status_code(res), explanation(res))
        raise Exception(error_msg)

def setup(client):
    info("Setting up ptg-sync test.")
    base_dir = "%s/%s" % (SURL_PREFIX, str(uuid.uuid4()))
    info("Creating base dir: " + base_dir)

    res = client.srmMkdir(base_dir)
    check_success(res, "Error creating %s" % base_dir)
    info("Base directory succesfully created.")

    surls = []

    for i in range(0, NUM_FILES):
        f_surl = "%s/f%d" % (base_dir, i)
        if i == 0:
            info("Creating surls like this: "+ f_surl)
        surls.append(f_surl)

    res = client.srmPtP(surls,[])
    while True:
        sres = client.srmSPtP(res)
        if status_code(sres) in WAITING_STATES:
            time.sleep(1)
        else:
            break

    check_success(sres, "Error in PtP for surls (only 5 shown out of %d): %s." % (len(surls),surls[0:5]))
    res = client.srmPd(surls, res.requestToken)
    check_success(res, "Error in PD for surls: %s" % surls)
    info("ptg-sync setup completed succesfully.")

    return base_dir,surls

def cleanup(client, base_dir):
    info("Cleaning up for ptg-sync test.")

    res = client.srmRmdir(base_dir, True)
    if status_code(res) != SRM_SUCCESS:
        raise Exception("srmRmdir failed for %s. %s %s" %(base_dir, status_code(res), explanation(res)))
    info("ptg-sync cleanup completed succesfully.")

def ptg_sync(client, base_dir):
    surls = compute_surls(base_dir)
    ptg_runner = ptg.TestRunner()
    ptg_res = ptg_runner(surls, [], client)
    sptg_runner = sptg.TestRunner()

    counter = 0

    while True:
        res =  sptg_runner(ptg_res, client)
        counter = counter + 1
        sc = status_code(res)
        debug("sPtG invocation %d status code: %s" % (counter, sc) )

        if sc not in WAITING_STATES:
            break
        else:
            if counter > SLEEP_THRESHOLD:
                debug("Going to sleep for %f seconds" % SLEEP_TIME)
                time.sleep(SLEEP_TIME)

    debug("SPTG result (after %d invocations): %s: %s" %
            (counter, res.returnStatus.statusCode, res.returnStatus.explanation))

class TestRunner:
    def __call__(self):
        try:
            test = Test(TestID.PTG_SYNC, "StoRM Sync PTG test")
            test.record(ptg_sync)
            client = SRMClientFactory.newSRMClient(SRM_ENDPOINT, PROXY_FILE)

            if DO_HANDSHAKE:
                client.srmPing();

            (base_dir, surls) = setup(client)
            ptg_sync(client, base_dir)
            cleanup(client, base_dir)

        except Exception, e:
            error("Error executing ptg-sync: %s" % traceback.format_exc())
