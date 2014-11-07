from common import TestID, load_common_properties, get_proxy_file_path
from exceptions import Exception
from gov.lbl.srm.StorageResourceManager import TStatusCode
from net.grinder.script import Test
from net.grinder.script.Grinder import grinder
from org.italiangrid.srm.client import SRMClientFactory
import ptg,rmdir,sptg,sptp,mkdir,ptp,pd
import random
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

# Proxy authorized to write on SRM/WEBDAV endpoints
PROXY_FILE      = get_proxy_file_path()

# SRM clients (one per configured frontend)
SRM_CLIENTS = []

def init_srm_clients():
    frontends = [f.strip() for f in props['ptg-sync.frontends'].split(',')]

    info("frontends: %s" % frontends)

    for f in frontends:
        endpoint = "https://%s" % f
        client = SRMClientFactory.newSRMClient(endpoint, PROXY_FILE)
        SRM_CLIENTS.append((endpoint,client))

    info("SRM clients: %s" % SRM_CLIENTS)

init_srm_clients()

# Common variables:
TEST_STORAGEAREA = props['common.test_storagearea']

## Endpoints
FILETRANSFER_ENDPOINT = "https://%s:%s" % (props['common.gridhttps_host'],props['common.gridhttps_ssl_port'])
SRM_ENDPOINT    = "srm://%s:%s" % (props['common.frontend_host'],props['common.frontend_port'])


# Test specific variables
TEST_DIRECTORY  = props['ptg-sync.test_directory']

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
NUM_FILES = int(props['ptg-sync.num_files'])

def get_client():
    return random.choice(SRM_CLIENTS)

def status_code(resp):
    return resp.returnStatus.statusCode

def explanation(resp):
    return resp.returnStatus.explanation

def compute_surls(base_dir):
    random_index = random.randrange(0, NUM_FILES)
    surl = "%s/f%d" % (base_dir, random_index)
    return [surl]

def check_success(res, msg):
    if status_code(res) != SRM_SUCCESS:
        error_msg = "%s. %s (expl: %s)" % (msg, status_code(res), explanation(res))
        raise Exception(error_msg)

def setup():

    info("Setting up ptg-sync test.")
    endpoint,client = get_client()

    debug("Client endpoint: %s" % endpoint)

    test_dir = "%s/%s/%s" % (SRM_ENDPOINT, TEST_STORAGEAREA, TEST_DIRECTORY)
    mkdir_runner = mkdir.TestRunner()
    res = mkdir_runner(test_dir,client)

    base_dir = "%s/%s" % (test_dir, str(uuid.uuid4()))
    info("Creating thread specific dir: " + base_dir)

    res = mkdir_runner(base_dir,client)
    check_success(res, "Error creating %s" % base_dir)
    info("Base directory succesfully created.")

    surls = []

    for i in range(0, NUM_FILES):
        f_surl = "%s/f%d" % (base_dir, i)
        if i == 0:
            info("Creating surls like this: "+ f_surl)
        surls.append(f_surl)

    ptp_runner = ptp.TestRunner()
    res = ptp_runner(surls,[],client)

    sptp_runner = sptp.TestRunner()

    while True:
        sres = sptp_runner(res,client)
        if status_code(sres) in WAITING_STATES:
            time.sleep(1)
        else:
            break

    check_success(sres, "Error in PtP for surls (only 5 shown out of %d): %s." % (len(surls),surls[0:5]))
    pd_runner = pd.TestRunner()
    res = pd_runner(surls,res.requestToken,client)

    check_success(res, "Error in PD for surls: %s" % surls)
    info("ptg-sync setup completed succesfully.")

    return base_dir,surls

def cleanup(base_dir):
    info("Cleaning up for ptg-sync test.")

    endpoint, client = get_client()

    rmdir_runner = rmdir.TestRunner()
    res = rmdir_runner(base_dir, client, True)

    if status_code(res) != SRM_SUCCESS:
        raise Exception("srmRmdir failed for %s. %s %s" %(base_dir, status_code(res), explanation(res)))
    info("ptg-sync cleanup completed succesfully.")

def ptg_sync(base_dir):
    endpoint, client = get_client()
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
            if DO_HANDSHAKE:
                get_client()[1].srmPing()

            (base_dir, surls) = setup()
            ptg_sync(base_dir)
            cleanup(base_dir)

        except Exception:
            error("Error executing ptg-sync: %s" % traceback.format_exc())
