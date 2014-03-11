from common import TestID, load_common_properties, get_proxy_file_path
from jarray import array
from net.grinder.script import Test
from net.grinder.script.Grinder import grinder
from gov.lbl.srm.StorageResourceManager import TStatusCode
from org.italiangrid.srm.client import SRMClient, SRMClientFactory
import ptp, sptp, pd, rm
import traceback
import time
import uuid

## This loads the base properties inside grinder properties
## Should be left at the top of the script execution
load_common_properties()

error           = grinder.logger.error
info            = grinder.logger.info
debug           = grinder.logger.debug

props           = grinder.properties

# Proxy authorized to write on SRM/WEBDAV endpoints
PROXY_FILE      = get_proxy_file_path()

# Common variables:
TEST_STORAGEAREA = props['common.test_storagearea']

## Endpoints
FRONTEND_ENDPOINT = "https://%s:%s" % (props['common.frontend_host'],props['common.frontend_port'])
SRM_ENDPOINT    = "srm://%s:%s" % (props['common.frontend_host'],props['common.frontend_port'])

# Test specific variables
TEST_DIRECTORY  = props['rm.test_directory']
TEST_NUMFILES   = int(props['rm.test_number_of_files'])

MAX_WAITING_TIME_IN_MSEC = int(props['rm.max_waiting_time_in_msec'])

WAITING_STATES  = [TStatusCode.SRM_REQUEST_QUEUED, TStatusCode.SRM_REQUEST_INPROGRESS]
SRM_SUCCESS     = TStatusCode.SRM_SUCCESS

SRM_CLIENT      = SRMClientFactory.newSRMClient(FRONTEND_ENDPOINT,PROXY_FILE)

def status_code(resp):
    return resp.returnStatus.statusCode

def explanation(resp):
    return resp.returnStatus.explanation

def check_success(res, msg):
    if status_code(res) != SRM_SUCCESS:
        error_msg = "%s. %s (expl: %s)" % (msg, status_code(res), explanation(res))
        raise Exception(error_msg)

def create_test_directory_if_needed(SRMclient):
    test_dir_surl = "%s/%s/%s" % (SRM_ENDPOINT, TEST_STORAGEAREA, TEST_DIRECTORY)
    SRMclient.srmMkdir(test_dir_surl)

def setup(client,num_files):
    info("Setting up rm test.")
    # create test base directory - no check success, if exists: ok
    create_test_directory_if_needed(client)
    # base name for files:
    target_file_name = str(uuid.uuid4());
    # create num_files files
    surls = []
    for i in range(0, num_files):
         target_file_surl = "%s/%s/%s/%s_%s" % (SRM_ENDPOINT, TEST_STORAGEAREA, TEST_DIRECTORY, target_file_name, i)
         surls.append(target_file_surl)
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
    info("rm setup completed successfully.")
    return surls

def rm_files(client, surls):
    info("Executing rm test.")
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

            surls = setup(SRM_CLIENT, TEST_NUMFILES)
            rm_files(SRM_CLIENT, surls)

        except Exception, e:
            error("Error executing rm-files: %s" % traceback.format_exc())