from common import Configuration, Utils, TestID
from exceptions import Exception
from gov.lbl.srm.StorageResourceManager import TStatusCode
from net.grinder.script import Test
from net.grinder.script.Grinder import grinder
import ptg,rmdir,sptg,sptp,mkdir,ptp,pd,rf
import random
import time
import traceback
import uuid

error          = grinder.logger.error
info           = grinder.logger.info
debug          = grinder.logger.debug
props          = grinder.properties

CONF           = Configuration()
UTILS          = Utils()

## This loads the base properties inside grinder properties
## Should be left at the top of the script execution

CONF.load_common_properties()

SRM_ENDPOINT,SRM_CLIENT = UTILS.get_SRM_client(CONF)

# Common variables:
TEST_STORAGEAREA = CONF.get_test_storagearea()

# Local variables:
WAITING_STATES = [TStatusCode.SRM_REQUEST_QUEUED, TStatusCode.SRM_REQUEST_INPROGRESS]
SRM_SUCCESS  = TStatusCode.SRM_SUCCESS

TEST_DIRECTORY = CONF.get_prop('TESTSUITE_TEST_DIRECTORY', props["ptg-sync.test_directory"])

# Start sleeping between sptg requests after this number
SLEEP_THRESHOLD = int(CONF.get_prop('TESTSUITE_TEST_SLEEP_THRESHOLD', props["ptg-sync.sleep_threshold"]))

## Sleep time (seconds)
SLEEP_TIME = float(CONF.get_prop('TESTSUITE_TEST_SLEEP_TIME', props["ptg-sync.sleep_time"]))

## Perform an srmPing before running the test to rule out the handshake time from the stats
DO_HANDSHAKE = bool(CONF.get_prop('TESTSUITE_TEST_DO_HANDSHAKE', props["ptg-sync.do_handshake"]))

## Number of files created in the ptg directory
NUM_FILES = int(CONF.get_prop('TESTSUITE_TEST_NUM_FILES', props["ptg-sync.num_files"]))

def status_code(resp):
    return resp.returnStatus.statusCode

def explanation(resp):
    return resp.returnStatus.explanation

def check_success(res, msg):
    if status_code(res) != SRM_SUCCESS:
        error_msg = "%s. %s (expl: %s)" % (msg, status_code(res), explanation(res))
        raise Exception(error_msg)

def setup():

    debug("Setting up ptg-sync test.")

    mkdir_runner  = mkdir.TestRunner()
    ptp_runner    = ptp.TestRunner()
    sptp_runner   = sptp.TestRunner()
    pd_runner     = pd.TestRunner()

    test_dir_surl = UTILS.get_surl(SRM_ENDPOINT, TEST_STORAGEAREA, TEST_DIRECTORY)
    debug("Creating test directory if it doesn't exist: " + test_dir_surl)
    mkdir_runner(test_dir_surl,SRM_CLIENT)

    base_dir_surl = "%s/%s" % (test_dir_surl, str(uuid.uuid4()))
    debug("Creating thread specific dir: " + base_dir_surl)
    res = mkdir_runner(base_dir_surl,SRM_CLIENT)
    check_success(res, "Error creating %s" % base_dir_surl)

    debug("Creating surls ... ")
    surls = []
    for i in range(0, NUM_FILES):
        f_surl = "%s/f%d" % (base_dir_surl, i)
        debug("Added SURL: %s" % f_surl)
        surls.append(f_surl)

    debug("Call srmPtP on SURLs ... ")
    res = ptp_runner(surls,[],SRM_CLIENT)

    while True:
        sres = sptp_runner(res,SRM_CLIENT)
        if status_code(sres) in WAITING_STATES:
            time.sleep(1)
        else:
            break

    check_success(sres, "Error in PtP for surls (only 5 shown out of %d): %s." % (len(surls),surls[0:5]))
    
    res = pd_runner(surls,res.requestToken,SRM_CLIENT)

    check_success(res, "Error in PD for surls: %s" % surls)
    debug("ptg-sync setup completed succesfully.")

    return base_dir_surl,surls

def cleanup(base_dir):
    debug("Cleaning up for ptg-sync test.")

    rmdir_runner = rmdir.TestRunner()
    res = rmdir_runner(base_dir, SRM_CLIENT, True)

    if status_code(res) != SRM_SUCCESS:
        raise Exception("srmRmdir failed for %s. %s %s" %(base_dir, status_code(res), explanation(res)))
    debug("ptg-sync cleanup completed succesfully.")

def ptg_sync(surls):
    
    surl = random.choice(surls)
    
    ptg_runner   = ptg.TestRunner()
    sptg_runner  = sptg.TestRunner()
    
    ptg_res = ptg_runner([surl], [], SRM_CLIENT)
    counter = 0

    token = ptg_res.requestToken
    while True:
        res =  sptg_runner(ptg_res, SRM_CLIENT)
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
        rf_res = rf_runner(surls[i],token,SRM_CLIENT)
        check_success(rf_res, "Error in RF for surl %s and token %s" % (surls[i], token))

class TestRunner:
    def __call__(self):
        try:
            test = Test(TestID.PTG_SYNC, "StoRM Sync PTG test")
            test.record(ptg_sync)
            if DO_HANDSHAKE:
                SRM_CLIENT.srmPing()

            (base_dir_surl, surls) = setup()
            ptg_sync(surls)
            cleanup(base_dir_surl)

        except Exception:
            error("Error executing ptg-sync: %s" % traceback.format_exc())
