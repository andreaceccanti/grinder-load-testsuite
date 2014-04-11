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
import ls, ptg, ptp, sptp, pd
import random
import string
import time
import traceback
import uuid
import os


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
TEST_DIRECTORY  = props['ptg_async.test_directory']

WAITING_STATES  = [TStatusCode.SRM_REQUEST_QUEUED, TStatusCode.SRM_REQUEST_INPROGRESS]
SRM_SUCCESS     = TStatusCode.SRM_SUCCESS

SURL            = "%s/%s/%s/%s" % (SRM_ENDPOINT, TEST_STORAGEAREA, TEST_DIRECTORY, "test_ptg.txt")

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

def setup(client):
    info("Setting up file-transfer-in test.")
    # create test directory without check failures
    create_test_directory_if_needed(client)
    # check if test file exists
    info("Check if SURL exists: %s" % SURL)
    ls_runner = ls.TestRunner()
    ls_res = ls_runner(SURL, client)
    if status_code(ls_res) != SRM_SUCCESS:
        ptp_runner = ptp.TestRunner()
        res = ptp_runner([SURL], [], client)
        sptp_runner = sptp.TestRunner()
        while True:
            sres = sptp_runner(res,client)
            if status_code(sres) in WAITING_STATES:
                time.sleep(1)
            else:
                break
        check_success(sres, "Error in PtP for surl: %s." % SURL)
        pd_runner = pd.TestRunner()
        res = pd_runner([SURL], res.requestToken, client)
        check_success(res, "Error in PD for surl: %s" % SURL)
        info("Target file successfully created.")
    info("ptg-async setup completed successfully.")

def do_prepare_to_get(SRM_client):
    ptg_runner = ptg.TestRunner()
    ptg_runner([SURL],[],SRM_client)

class TestRunner:

    def __init__(self):
        self.SRMclient = SRMClientFactory.newSRMClient(FRONTEND_ENDPOINT,PROXY_FILE)
        setup(self.SRMclient)

	def __call__(self):
		try:
			test = Test(TestID.PTG_ASYNC, "StoRM ptg-async without release or file transfer")
			test.record(do_prepare_to_get)
			do_prepare_to_get(self.SRMclient)
		except Exception, e:
			error("Error executing ptg-async: %s" % traceback.format_exc())
