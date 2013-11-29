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
import ptp
import random
import sptp
import pd
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
BASE_FILE_PATH = props['ptp-sync.base_file_path']

SRM_ENDPOINT   = "https://%s" % FE_HOST
SURL_PREFIX    = "srm://%s/%s" % (FE_HOST, BASE_FILE_PATH)

WAITING_STATES = [TStatusCode.SRM_REQUEST_QUEUED, TStatusCode.SRM_REQUEST_INPROGRESS]

# Start sleeping between sptp requests after this number
SLEEP_THRESHOLD = int(props['ptp-sync.sleep_threshold'])

## Sleep time (seconds)
SLEEP_TIME = float(props['ptp-sync.sleep_time'])

## Perform an srmPing before running the test to
## rule out the handshake time from the stats
DO_HANDSHAKE = bool(props['ptp-sync.do_handshake'])

def status_code(resp):
    return resp.returnStatus.statusCode

def compute_surls():
    ## Creates a random UUID
    rand_uuid = uuid.uuid4()
    surl = "%s/%s" % (SURL_PREFIX, str(rand_uuid))
    return [surl]

def ptp_sync(client):
    surls = compute_surls()
    ptp_runner = ptp.TestRunner()
    ptp_res = ptp_runner(surls, [], client)
    sptp_runner = sptp.TestRunner()

    counter = 0

    while True:
        res =  sptp_runner(ptp_res, client)
        counter = counter + 1
        sc = status_code(res)
        debug("sPtP invocation %d status code: %s" % (counter, sc) )

        if sc not in WAITING_STATES:
            break
        else:
            if counter > SLEEP_THRESHOLD:
                debug("Going to sleep for %f seconds" % SLEEP_TIME)
                time.sleep(SLEEP_TIME)

    debug("SPTP result (after %d invocations): %s: %s" %
            (counter, res.returnStatus.statusCode, res.returnStatus.explanation))

    pd_runner = pd.TestRunner()
    res = pd_runner(surls, ptp_res.requestToken, client)

    if status_code(res) != TStatusCode.SRM_SUCCESS:
        msg = "PutDone failure on surl(s): %s" % surls
        error(msg)
        raise Error(msg)

    return surls

def cleanup(client, surls):
    res = client.srmRm(surls)
    if res.returnStatus.statusCode != TStatusCode.SRM_SUCCESS:
        msg = "Error cleaning up surl(s): %s" % surls
        error(msg)
        raise Exception(msg)

    debug("Cleaned up %s" % surls)

class TestRunner:
    def __call__(self):
        try:
            test = Test(TestID.PTP_SYNC, "StoRM Sync PTP test")
            test.record(ptp_sync)
            client = SRMClientFactory.newSRMClient(SRM_ENDPOINT, PROXY_FILE)

            if DO_HANDSHAKE:
                client.srmPing();

            surls = ptp_sync(client)
            cleanup(client, surls)

        except Exception, e:
            error("Error executing ptp-sync: %s" % traceback.format_exc())
            raise
