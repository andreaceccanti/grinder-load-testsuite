from common import TestID, load_common_properties, get_proxy_file_path
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
from org.italiangrid.dav.client import WebDAVClient, WebDAVClientFactory
import ptg, sptg, rf, ptp, sptp, pd, rm, http_get
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
FILETRANSFER_ENDPOINT = "https://%s:%s" % (props['common.gridhttps_host'],props['common.gridhttps_ssl_port'])
FRONTEND_ENDPOINT = "https://%s:%s" % (props['common.frontend_host'],props['common.frontend_port'])
SRM_ENDPOINT    = "srm://%s:%s" % (props['common.frontend_host'],props['common.frontend_port'])

# Test specific variables
TEST_DIRECTORY  = props['ftin.test_directory']
TRANSFER_PROTOCOL = props['ftin.transfer_protocol']

## Start sleeping between sptg requests after this number
SLEEP_THRESHOLD = int(props['ftin.sleep_threshold'])

## Sleep time (seconds)
SLEEP_TIME      = float(props['ftin.sleep_time'])

## Setup once: setup done at init time or each run
SETUP_ONCE      = props['ftin.setup_once']

WAITING_STATES  = [TStatusCode.SRM_REQUEST_QUEUED, TStatusCode.SRM_REQUEST_INPROGRESS]
SRM_SUCCESS     = TStatusCode.SRM_SUCCESS


def status_code(resp):
    return resp.returnStatus.statusCode

def explanation(resp):
    return resp.returnStatus.explanation

def check_success(res, msg):
    if status_code(res) != SRM_SUCCESS:
        error_msg = "%s. %s (expl: %s)" % (msg, status_code(res), explanation(res))
        raise Exception(error_msg)

def check_http_success(statusCode, expected_code, error_msg):
    if (statusCode != expected_code):
        msg = "%s. Status code is %s instead of %s" % (error_msg, statusCode, expected_code)
        raise Exception(msg)

def create_test_directory_if_needed(SRMclient):
    test_dir_surl = "%s/%s/%s" % (SRM_ENDPOINT, TEST_STORAGEAREA, TEST_DIRECTORY)
    SRMclient.srmMkdir(test_dir_surl)

def setup(client):
    info("Setting up file-transfer-in test.")
    
    target_file_name = str(uuid.uuid4());
    target_file_surl = "%s/%s/%s/%s" % (SRM_ENDPOINT, TEST_STORAGEAREA, TEST_DIRECTORY, target_file_name)

    info("Creating target file: %s" % target_file_surl)

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
    check_success(res, "Error in PD for surl: " + target_file_surl)

    info("Target file successfully created.")

    info("file-transfer-in setup completed successfully.")
    return target_file_surl

def cleanup(client, target_file_surl):
    info("Cleaning up for file-transfer-in test.")
    res = client.srmRm([target_file_surl])
    if status_code(res) != SRM_SUCCESS:
        raise Exception("srmRm failed for %s. %s %s" % (target_file_surl, status_code(res), explanation(res)))
    info("file-transfer-in cleanup completed successfully.")

def do_prepare_to_get(SRM_client,surl,transfer_protocol):

    ptg_runner = ptg.TestRunner()
    ptg_res = ptg_runner([surl],[transfer_protocol],SRM_client)
    
    sptg_runner = sptg.TestRunner()
    counter=0
    while True:
        res = sptg_runner(ptg_res,SRM_client)
        sc = res.returnStatus.statusCode
        counter+=1
        info("sPtG invocation %d status code: %s" % (counter,sc) )
        if sc not in WAITING_STATES:
            break
        else:
            if counter > SLEEP_THRESHOLD:
                debug("Going to sleep for %d seconds" % SLEEP_TIME)
                time.sleep(SLEEP_TIME)

    info("SPTG result (after %d invocations): %s: %s" % (counter, res.returnStatus.statusCode, res.returnStatus.explanation))
    turl = res.getArrayOfFileStatuses().getStatusArray(0).getTransferURL()
    return (ptg_res.requestToken,turl.toString())

def do_release_file(SRM_client,surl,token):

    rf_runner = rf.TestRunner()
    rf_res = rf_runner(surl,token,SRM_client)
    check_success(rf_res, "Error in RF for surl %s and token %s" % (surl, token))


def file_transfer_in(SRM_client, HTTP_client, target_file_surl, transfer_protocol):

    (token,turl) = do_prepare_to_get(SRM_client,target_file_surl,transfer_protocol)

    http_get_runner = http_get.TestRunner()
    statusCode = http_get_runner(turl,HTTP_client)
    check_http_success(statusCode, 200, "Error in HTTP GET")

    do_release_file(SRM_client,target_file_surl,token)


class TestRunner:

	def __init__(self):
		self.SRMclient = SRMClientFactory.newSRMClient(FRONTEND_ENDPOINT,PROXY_FILE)
		self.HTTPclient = WebDAVClientFactory.newWebDAVClient(FILETRANSFER_ENDPOINT,PROXY_FILE)
		create_test_directory_if_needed(self.SRMclient)
		if (SETUP_ONCE == "yes"):
			self.target_file_surl = setup(self.SRMclient)

	def __call__(self):
		try:
			if (SETUP_ONCE != "yes"):
				self.target_file_surl = setup(self.SRMclient)
			test = Test(TestID.TXFER_IN, "StoRM file-transfer IN")
			test.record(file_transfer_in)
			file_transfer_in(self.SRMclient, self.HTTPclient, self.target_file_surl, TRANSFER_PROTOCOL)
			if (SETUP_ONCE != "yes"):
				cleanup(self.SRMclient, self.target_file_surl)
		except Exception, e:
			error("Error executing file-transfer-in: %s" % traceback.format_exc())

	def __del__(self):
		if (SETUP_ONCE == "yes"):
			cleanup(self.SRMclient, self.target_file_surl)
