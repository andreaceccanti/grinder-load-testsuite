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

DIRECTORY_NAME  = "testdir"

def generateSURLs(height):
    surls = []
    parent_surl = "%s/%s/%s" % (SRM_ENDPOINT, TEST_STORAGEAREA, TEST_DIRECTORY)
    surls.append(parent_surl)
    for i in range(1, height + 1):
        surl = "%s/%s" % (parent_surl,DIRECTORY_NAME)
        surls.append(surl)
        parent_surl = surl
    return surls

SURLS           = generateSURLs(TEST_DIR_HEIGHT)

SRM_SUCCESS     = TStatusCode.SRM_SUCCESS
WAITING_STATES  = [TStatusCode.SRM_REQUEST_QUEUED, TStatusCode.SRM_REQUEST_INPROGRESS]

SRM_CLIENT      = SRMClientFactory.newSRMClient(FRONTEND_ENDPOINT,PROXY_FILE)

DO_INIT         = 1

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

    target_dir_name = DIRECTORY_NAME;
    target_dir_surl = "%s/%s" % (parentdir_surl, target_dir_name)
    if (DO_SETUP == "yes"):
        client.srmMkdir(target_dir_surl)
    return target_dir_surl

def upload_file(parentdir_surl,filename,client):

    debug("Upload file %s into %s" % (filename,parentdir_surl))
    target_file_surl = "%s/%s" % (parentdir_surl, filename)
    if (DO_SETUP == "yes"):
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
    debug("File %s successfully uploaded." % filename)

def fill_test_directory(current_level,parent_surl,width,height,client):
    
    next_surl = create_directory(parent_surl,client)
    for i in range(1, width + 1):
        filename = str(uuid.uuid4());
        upload_file(parent_surl,filename,client)
    current_level = current_level + 1
    if (current_level < height):
        fill_test_directory(current_level, next_surl, width, height, client)

def setup(SRM_client):

    info("Setting up ls test.")
    create_test_directory_if_needed(SRM_client)
    base_dir_surl = "%s/%s/%s" % (SRM_ENDPOINT, TEST_STORAGEAREA, TEST_DIRECTORY)
    SURLS.append(base_dir_surl)
    fill_test_directory(0,base_dir_surl,TEST_DIR_WIDTH,TEST_DIR_HEIGHT,SRM_client)
    info("ls setup completed successfully.")

def ls_test(client):

    i = random.randint(1, TEST_DIR_HEIGHT) - 1
    debug("i = %s" % i)
    base_dir_surl = SURLS[i]
    #base_dir_surl = "%s/%s/%s" % (SRM_ENDPOINT, TEST_STORAGEAREA, TEST_DIRECTORY)
    ls_runner = ls.TestRunner()
    ls_res = ls_runner(base_dir_surl, client)
    check_success(ls_res, "Ls failure on surl: %s" % base_dir_surl)


class TestRunner:

    def __init__(self):
        self.SetupCompleteBarrier = grinder.barrier("Init barrier")

    def __call__(self):
        
        if (grinder.getRunNumber() == 0):
            debug("init method for thread %s process %s agent %s" % (grinder.getThreadNumber(),grinder.getProcessNumber(),grinder.getAgentNumber()))
            id = grinder.getThreadNumber() + grinder.getProcessNumber() + grinder.getAgentNumber()
            debug("id is %s" % id)
            if (id == 0):
                 setup(SRM_CLIENT)
                 info("SURLS: %s" % SURLS)
            debug("before waiting")
            self.SetupCompleteBarrier.await()
            debug("after waiting")

        try:
            test = Test(TestID.LS_TEST, "StoRM LS test")
            test.record(ls_test)

            ls_test(SRM_CLIENT)

        except Exception, e:
            error("Error executing ls test: %s" % traceback.format_exc())
            raise
