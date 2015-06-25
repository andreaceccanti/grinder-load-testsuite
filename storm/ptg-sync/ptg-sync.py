from common import *
from exceptions import Exception
from gov.lbl.srm.StorageResourceManager import TStatusCode
from net.grinder.script import Test
from net.grinder.script.Grinder import grinder
from org.italiangrid.srm.client import SRMClientFactory
import ptg,rmdir,sptg,sptp,mkdir,ptp,pd,rf
import random
import time
import traceback
import uuid

error          = grinder.logger.error
info           = grinder.logger.info
debug          = grinder.logger.debug
props          = grinder.properties

def get_test_directory():
    return get_prop('TESTSUITE_TEST_DIRECTORY', props["ptg-sync.test_directory"])

def get_test_sleep_threshold():
    return int(get_prop('TESTSUITE_TEST_SLEEP_THRESHOLD', props["ptg-sync.sleep_threshold"]))

def get_test_sleep_time():
    return float(get_prop('TESTSUITE_TEST_SLEEP_TIME', props["ptg-sync.sleep_time"]))

def get_test_do_handshake():
    return bool(get_prop('TESTSUITE_TEST_DO_HANDSHAKE', props["ptg-sync.do_handshake"]))

def get_test_num_files():
    return int(get_prop('TESTSUITE_TEST_NUM_FILES', props["ptg-sync.num_files"]))

def init_srm_clients(fe_list):
    clients = []
    frontends = [f.strip() for f in fe_list.split(',')]
    for f in frontends:
        client = SRMClientFactory.newSRMClient("https://%s" % f, get_proxy_file_path())
        clients.append((f,client))
    return clients

## This loads the base properties inside grinder properties
## Should be left at the top of the script execution
load_common_properties()

# SRM clients (one per configured frontend)
FE_LIST = get_storm_fe_endpoint_list()
info("Frontend list: %s" % FE_LIST)
SRM_CLIENTS = init_srm_clients(FE_LIST)
info("SRM clients: %s" % SRM_CLIENTS)

# Common variables:
TEST_STORAGEAREA = get_test_storagearea()

WAITING_STATES = [TStatusCode.SRM_REQUEST_QUEUED, TStatusCode.SRM_REQUEST_INPROGRESS]
SRM_SUCCESS  = TStatusCode.SRM_SUCCESS

# Start sleeping between sptg requests after this number
SLEEP_THRESHOLD = get_test_sleep_threshold()
info("SLEEP_THRESHOLD = %s" % SLEEP_THRESHOLD)

## Sleep time (seconds)
SLEEP_TIME = get_test_sleep_time()
info("SLEEP_TIME = %s" % SLEEP_TIME)

## Perform an srmPing before running the test to
## rule out the handshake time from the stats
DO_HANDSHAKE = get_test_do_handshake()
info("DO_HANDSHAKE = %s" % DO_HANDSHAKE)

## Number of files created in the ptg directory
NUM_FILES = get_test_num_files()
info("NUM_FILES = %s" % NUM_FILES)

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

    test_dir_surl = get_surl(endpoint, get_test_storagearea(), get_test_directory())

    mkdir_runner = mkdir.TestRunner()
    res = mkdir_runner(test_dir_surl,client)

    base_dir_surl = "%s/%s" % (test_dir_surl, str(uuid.uuid4()))
    info("Creating thread specific dir: " + base_dir_surl)

    res = mkdir_runner(base_dir_surl,client)
    check_success(res, "Error creating %s" % base_dir_surl)
    info("Base directory succesfully created.")

    surls = []

    for i in range(0, NUM_FILES):
        f_surl = "%s/f%d" % (base_dir_surl, i)
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

    return base_dir_surl,surls

def cleanup(base_dir):
    info("Cleaning up for ptg-sync test.")

    endpoint, client = get_client()

    rmdir_runner = rmdir.TestRunner()
    res = rmdir_runner(base_dir, client, True)

    if status_code(res) != SRM_SUCCESS:
        raise Exception("srmRmdir failed for %s. %s %s" %(base_dir, status_code(res), explanation(res)))
    info("ptg-sync cleanup completed succesfully.")

def ptg_sync(base_dir_surl):
    endpoint, client = get_client()
    surls = compute_surls(base_dir_surl)
    ptg_runner = ptg.TestRunner()
    ptg_res = ptg_runner(surls, [], client)
    sptg_runner = sptg.TestRunner()

    counter = 0

    token = ptg_res.requestToken
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

    for i in range(0, len(surls)):
        rf_runner = rf.TestRunner()
        rf_res = rf_runner(surls[i],token,client)
        check_success(rf_res, "Error in RF for surl %s and token %s" % (surls[i], token))

class TestRunner:
    def __call__(self):
        try:
            test = Test(TestID.PTG_SYNC, "StoRM Sync PTG test")
            test.record(ptg_sync)
            if DO_HANDSHAKE:
                get_client()[1].srmPing()

            (base_dir_surl, surls) = setup()
            info("base_dir_surl = %s" % base_dir_surl)
            ptg_sync(base_dir_surl)
            cleanup(base_dir_surl)

        except Exception:
            error("Error executing ptg-sync: %s" % traceback.format_exc())
