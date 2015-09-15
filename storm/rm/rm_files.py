from common import TestID, Configuration, Utils
from jarray import array
from net.grinder.script import Test
from net.grinder.script.Grinder import grinder
from gov.lbl.srm.StorageResourceManager import TStatusCode
from org.italiangrid.srm.client import SRMClient, SRMClientFactory
import mkdir, ptp, sptp, pd
import traceback
import time
import random
import uuid

error           = grinder.logger.error
info            = grinder.logger.info
debug           = grinder.logger.debug

props           = grinder.properties

conf           = Configuration()
utils          = Utils()

# Get common variables:
SRM_CLIENTS = utils.get_srm_clients(conf)
TEST_STORAGEAREA = conf.get_test_storagearea()

# Test specific variables
TEST_DIRECTORY  = props['rm.test_directory']
TEST_NUMFILES   = int(props['rm.test_number_of_files'])
MAX_WAITING_TIME_IN_MSEC = int(props['rm.max_waiting_time_in_msec'])

WAITING_STATES  = [TStatusCode.SRM_REQUEST_QUEUED, TStatusCode.SRM_REQUEST_INPROGRESS]
SRM_SUCCESS     = TStatusCode.SRM_SUCCESS

def get_client():
    return random.choice(SRM_CLIENTS)

TEST_DIRECTORY_SURL = utils.get_surl(get_client()[0], TEST_STORAGEAREA, TEST_DIRECTORY)

def initSURLs(num_files):
    surls = []
    target_file_name = str(uuid.uuid4());
    for i in range(0, num_files):
        surl = "%s/%s_%s" % (TEST_DIRECTORY_SURL, target_file_name, i)
        surls.append(surl)
        debug("appended: %s" % surl)
    return surls

SURLS = initSURLs(TEST_NUMFILES)



def status_code(resp):
    return resp.returnStatus.statusCode

def explanation(resp):
    return resp.returnStatus.explanation

def check_success(res, msg):
    if status_code(res) != SRM_SUCCESS:
        error_msg = "%s. %s (expl: %s)" % (msg, status_code(res), explanation(res))
        raise Exception(error_msg)

def create_directory(client, surl):
    mkdir_runner = mkdir.TestRunner()
    res = mkdir_runner(surl, client)
    debug("mkdir returned status: %s (expl: %s)" % (status_code(res), explanation(res)))

def create_files(client, surls):
    debug("Creating target file(s): %s " % surls)
    ptp_runner = ptp.TestRunner()
    res = ptp_runner(surls, [], client)
    sptp_runner = sptp.TestRunner()
    while True:
        sres = sptp_runner(res,client)
        if status_code(sres) in WAITING_STATES:
            time.sleep(1)
        else:
            break
    check_success(sres, "Error in PtP for surl(s): %s." % surls)
    pd_runner = pd.TestRunner()
    res = pd_runner(surls, res.requestToken, client)
    check_success(res, "Error in PD for surl(s): %s" % surls)
    debug("Target file(s) successfully created.")

def setup(surls):
    info("Setting up rm test.")
    client = get_client()[1] 
    create_directory(client, TEST_DIRECTORY_SURL)
    create_files(client, surls)
    info("rm setup completed successfully.")

def rm_files(surls):
    info("Executing rm test.")
    client = get_client()[1]
    rm_runner = rm.TestRunner()
    res = rm_runner(surls, client)
    statuses = res.getArrayOfFileStatuses().getStatusArray() 
    for s in statuses:
        debug("%s -> %s" %(s.getSurl(),s.getStatus().getStatusCode()))
    if status_code(res) != SRM_SUCCESS:
        raise Exception("srmRm failed for %s. %s %s" % (surls, status_code(res), explanation(res)))
    info("Rm test completed.")

class TestRunner:

    def __call__(self):
        try:
            test = Test(TestID.RM_FILES, "StoRM srmRm files")
            test.record(rm_files)

            setup(SURLS)
            rm_files(SURLS)

        except Exception, e:
            error("Error executing rm-files: %s" % traceback.format_exc())