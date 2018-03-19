from common import *
from srm import *
from exceptions import Exception
from jarray import array
from java.io import FileInputStream
from net.grinder.script import Test
from net.grinder.script.Grinder import grinder
import random
import string
import time
import traceback
import uuid

error          = grinder.logger.error
info           = grinder.logger.info
debug          = grinder.logger.debug

props          = grinder.properties

utils           = Utils(grinder.properties)

file_to_upload = "/tmp/prova.txt"

# Common variables:
TEST_STORAGEAREA = props['common.test_storagearea']

# Test specific variables
TEST_DIRECTORY      = props['ptp_pd.test_directory']
SLEEP_THRESHOLD     = int(props['ptp_pd.sleep_threshold'])
SLEEP_TIME          = float(props['ptp_pd.sleep_time'])
TEST_FILE_LIFETIME  = int(props['ptp_pd.pinLifetime_sec'])
TEST_FILENAME       = "%s/%s/%s" % (TEST_STORAGEAREA, TEST_DIRECTORY, str(uuid.uuid4()))
TEST_NUM_FILES      = int(props['ptp_pd.numfiles'])

def get_base_dir():
    return "%s/%s" % (TEST_STORAGEAREA, TEST_DIRECTORY)

def do_prepare_to_put(client,surls):
    (token, response) = srmPtP(client, surls, [], True, SLEEP_THRESHOLD, SLEEP_TIME)
    statuses = response.getArrayOfFileStatuses().getStatusArray()
    turls = []
    surl_attr_names = ["transferURL"]
    for s in statuses:
        info(str(s))
        fn = [ x for x in surl_attr_names if x in dir(s) ]
        turl = getattr(s, fn[0])
        turls.append(str(turl))
    return token, turls

def do_put_done(client, surls, token):
    response = srmPd(client, surls, token)
    log_result_file_status(response)

def setup_thread_dir():
    debug("Setup ptp_pd thread dir test ...")
    endpoint, client = utils.get_srm_client()

    base_dir = get_base_dir()
    agent_dir = "%s/%s" % (base_dir, "a" + str(grinder.getAgentNumber()))
    process_dir = "%s/%s" % (agent_dir, "p" + str(grinder.getProcessNumber()))
    thread_dir = "%s/%s" % (process_dir, "t" + str(grinder.getThreadNumber()))

    info("Creating remote test directory ... " + base_dir)
    srmMkDir(client, get_surl(endpoint, base_dir))
    info("Creating remote test directory ... " + agent_dir)
    srmMkDir(client, get_surl(endpoint, agent_dir))
    info("Creating remote test directory ... " + process_dir)
    srmMkDir(client, get_surl(endpoint, process_dir))
    info("Creating remote test directory ... " + thread_dir)
    srmMkDir(client, get_surl(endpoint, thread_dir))

    debug("setup ptp_pd completed successfully.")
    return thread_dir

def ptp_pd(client,surls):
    debug("PtP on remote test files ... ")
    token, turls = do_prepare_to_put(client, surls)
    for i in range(0, len(turls)):
        os.system("globus-url-copy -vb file://" + file_to_upload + " " + turls[i])
    #grinder.sleep(TEST_FILE_LIFETIME*1000)
    debug("Pd on remote test files ... " + token)
    do_put_done(client, surls, token)

def run_setup(endpoint, thread_dir):
    debug("Setup run " + str(grinder.getRunNumber()) + " ...")

    surls = []
    for i in range(1, TEST_NUM_FILES + 1):
        file_index = TEST_NUM_FILES * grinder.getRunNumber() + i
        surl = get_surl(endpoint, "%s/file_%d" % (thread_dir, file_index))
        surls.append(surl)
        debug("appended: %s" % surl)

    return surls


class TestRunner:

    def __init__(self):

        self.thread_dir = setup_thread_dir()
        info("Thread dir is: " + self.thread_dir)

    def __call__(self):

        try:

            endpoint, client = utils.get_srm_client()

            test = Test(TestID.PTP_PD, "StoRM PtP-PD test")
            test.record(ptp_pd)

            surls = run_setup(endpoint, self.thread_dir)
            ptp_pd(client, surls)

        except Exception, e:
            error("Error executing ptp_pd: %s" % traceback.format_exc())
            raise

    def __del__(self):
        info("srmRmDir %s ... " % self.thread_dir)
        endpoint, client = utils.get_srm_client()
        surl = get_surl(endpoint, self.thread_dir)
    	response = client.srmRmdir(surl, True)
    	info("srmRmDir %s response is %s %s" % (surl, response.returnStatus.statusCode, response.returnStatus.explanation))
