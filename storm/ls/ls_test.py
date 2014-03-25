from common import TestID, load_common_properties, get_proxy_file_path
from eu.emi.security.authn.x509.impl import PEMCredential
from exceptions import Exception
from gov.lbl.srm.StorageResourceManager import TStatusCode
from jarray import array
from java.io import FileInputStream
from javax.net.ssl import X509ExtendedKeyManager
from net.grinder.script import Test
from net.grinder.script.Grinder import grinder
from org.italiangrid.srm.client import SRMClient, SRMClientFactory
import mkdir, ptp, sptp, pd, ls
import random
import string
import time
import traceback
import uuid
import os


## This loads the base properties inside grinder properties
## Should be left at the top of the script execution
load_common_properties()

error          = grinder.logger.error
info           = grinder.logger.info
debug          = grinder.logger.debug

props          = grinder.properties

# Proxy authorized to write on SRM/WEBDAV endpoints
PROXY_FILE      = get_proxy_file_path()

# Get common variables:
TEST_STORAGEAREA = props['common.test_storagearea']

## Endpoints
FRONTEND_ENDPOINT = "https://%s:%s" % (props['common.frontend_host'],props['common.frontend_port'])
SRM_ENDPOINT    = "srm://%s:%s" % (props['common.frontend_host'],props['common.frontend_port'])

# Test specific variables
TEST_DIRECTORY  = props['ls.test_directory']
TEST_DIR_WIDTH  = int(props['ls.test_directory_width'])
TEST_DIR_HEIGHT = int(props['ls.test_directory_height'])

DO_SETUP        = props['ls.do_setup']
DO_CLEANUP      = props['ls.do_cleanup']

DIRECTORY_NAME  = "testdir"
FILE_PREFIX  = "file"

SRM_SUCCESS     = TStatusCode.SRM_SUCCESS
WAITING_STATES  = [TStatusCode.SRM_REQUEST_QUEUED, TStatusCode.SRM_REQUEST_INPROGRESS]

SRM_CLIENT      = SRMClientFactory.newSRMClient(FRONTEND_ENDPOINT,PROXY_FILE)

TEST_DIRECTORY_SURL = "%s/%s/%s" % (SRM_ENDPOINT, TEST_STORAGEAREA, TEST_DIRECTORY)

def status_code(resp):

    return resp.returnStatus.statusCode

def explanation(resp):

    return resp.returnStatus.explanation

def check_success(res, msg):

    if status_code(res) != SRM_SUCCESS:
        error_msg = "%s. %s (expl: %s)" % (msg, status_code(res), explanation(res))
        raise Exception(error_msg)

def create_test_directory_if_needed(SRM_client):

    test_dir_surl = "%s/%s/%s" % (SRM_ENDPOINT, TEST_STORAGEAREA, TEST_DIRECTORY)
    SRM_client.srmMkdir(test_dir_surl)

def create_directory(parentdir_surl,client):
    target_dir_surl = "%s/%s" % (parentdir_surl, DIRECTORY_NAME)
    mkdir_runner = mkdir.TestRunner()
    res = mkdir_runner(target_dir_surl, client)
    debug("mkdir returned status: %s (expl: %s)" % (status_code(res), explanation(res)))
    info("CREATED DIR %s" % parentdir_surl)
    return target_dir_surl

def upload_file(parentdir_surl,filename,client):

    debug("Upload file %s into %s" % (filename,parentdir_surl))
    target_file_surl = "%s/%s" % (parentdir_surl, filename)
    ptp_runner = ptp.TestRunner()
    res = ptp_runner([target_file_surl], [], client)
    sptp_runner = sptp.TestRunner()
    while True:
        sres = sptp_runner(res,client)
        if status_code(sres) in WAITING_STATES:
            time.sleep(1)
        else:
            break
    check_success(sres, "Error in PtP for surl: %s." % target_file_surl)
    pd_runner = pd.TestRunner()
    res = pd_runner([target_file_surl], res.requestToken, client)
    check_success(res, "Error in PD for surl: %s" % target_file_surl)
    info("UPLOADED %s to %s" % (filename, target_file_surl))
    debug("File %s successfully uploaded." % filename)
    return target_file_surl

def fill_test_directory(current_level,parent_surl,width,height,client):
    next_surl = create_directory(parent_surl, client)
    for i in range(1, width + 1):
        file_name = "%s_%d" % (FILE_PREFIX, i)
        upload_file(parent_surl,file_name,client)
    current_level = current_level + 1
    if (current_level < height):
        fill_test_directory(current_level, next_surl, width, height, client)

def generateSURLs(height, width):
    surls = []
    parent_surl = TEST_DIRECTORY_SURL
    surls.append(parent_surl)
    debug("appended: %s" % parent_surl)
    for i in range(1, height + 1):
        dsurl = "%s/%s" % (parent_surl, DIRECTORY_NAME)
        surls.append(dsurl)
        debug("appended: %s" % dsurl)
        for j in range(1, width + 1):
            fsurl = "%s/%s_%d" % (parent_surl, FILE_PREFIX, j)
            surls.append(fsurl)
            debug("appended: %s" % fsurl)
        parent_surl = dsurl
    return surls

def setup(client, base_dir_surl, height, width):

    info("Setting up ls test.")
    create_test_directory_if_needed(client)
    if (DO_SETUP == "yes"):
        fill_test_directory(0, base_dir_surl, width, height, client)
    info("ls setup completed successfully.")

def cleanup(client, base_dir_surl):

    info("Cleaning up ls test.")
    if (DO_CLEANUP == "yes"):
        client.srmRmdir(base_dir_surl, 1)
    info("ls cleanup completed successfully.")

def ls_test(client, surl):

    ls_runner = ls.TestRunner()
    ls_res = ls_runner(surl, client)
    check_success(ls_res, "Ls failure on surl: %s" % surl)


class TestRunner:

    def __init__(self):
        self.surls = generateSURLs(TEST_DIR_HEIGHT, TEST_DIR_WIDTH)
        debug("SURLS: %s" % self.surls)
        self.SetupCompleteBarrier = grinder.barrier("Init barrier")
        self.ReadyToCleanUpBarrier = grinder.barrier("Cleanup barrier")
        self.numruns = int(props["grinder.runs"])

    def __call__(self):
        
        if (self.isFirstRun()):
            if (self.isTheInitializer()):
                 setup(SRM_CLIENT,TEST_DIRECTORY_SURL,TEST_DIR_HEIGHT,TEST_DIR_WIDTH)
                 info("A:%s,P:%s,T:%s setup done!")
            debug("waiting all the other threads")
            self.SetupCompleteBarrier.await()
            debug("ok, go!")

        try:
            test = Test(TestID.LS_TEST, "StoRM LS test")
            test.record(ls_test)
            i = random.randint(1, TEST_DIR_HEIGHT*TEST_DIR_WIDTH) - 1
            info("[i = %d] Ls on %s" % (i, self.surls[i]))
            ls_test(SRM_CLIENT, self.surls[i])

        except Exception, e:
            error("Error executing ls test: %s" % traceback.format_exc())
            raise

        if (self.isLastRun()):
            debug("waiting all the other threads")
            self.ReadyToCleanUpBarrier.await()
            if (self.isTheInitializer()):
                 cleanup(SRM_CLIENT,TEST_DIRECTORY_SURL)
                 info("A:%s,P:%s,T:%s cleanup done!")
            debug("ok, finished!")

    def isFirstRun(self):
        return grinder.getRunNumber() == 0

    def isLastRun(self):
        return grinder.getRunNumber() == (self.numruns - 1)

    def isTheInitializer(self):
        debug("I am thread %s process %s agent %s" % (grinder.getThreadNumber(),grinder.getProcessNumber(),grinder.getAgentNumber()))
        id = grinder.getThreadNumber() + grinder.getProcessNumber() + grinder.getAgentNumber()
        debug("My id is %s" % id)
        return id == 0