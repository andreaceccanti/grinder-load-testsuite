from common import *
from exceptions import Exception
from gov.lbl.srm.StorageResourceManager import TStatusCode
from jarray import array
from java.io import FileInputStream
from net.grinder.plugin.http import HTTPRequest
from net.grinder.script import Test
from net.grinder.script.Grinder import grinder
from org.italiangrid.srm.client import SRMClient, SRMClientFactory
from org.italiangrid.dav.client import WebDAVClient, WebDAVClientFactory
import ptg, sptg, rf, ptp, sptp, pd, rm, http_get, mkdir
import string
import time
import traceback
import uuid
import os

error = grinder.logger.error
info = grinder.logger.info
debug = grinder.logger.debug

props = grinder.properties

utils = Utils(grinder.properties)

# Common variables:
TEST_STORAGEAREA = props['common.test_storagearea']

# Test specific variables
TEST_DIRECTORY = props['ft_in.test_directory']
TRANSFER_PROTOCOL = props['ft_in.transfer_protocol']
SLEEP_THRESHOLD = int(props['ft_in.sleep_threshold'])
SLEEP_TIME = float(props['ft_in.sleep_time'])

WAITING_STATES = [TStatusCode.SRM_REQUEST_QUEUED, TStatusCode.SRM_REQUEST_INPROGRESS]
SRM_SUCCESS = TStatusCode.SRM_SUCCESS

def get_srm_client():
    
    return utils.get_srm_client()

def get_dav_client():
    
    return utils.get_dav_client()

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

def create_remote_directory(file_path):
    
    endpoint, client = get_srm_client()
    surl = get_surl(endpoint, TEST_STORAGEAREA, file_path)
       
    mkdir_runner = mkdir.TestRunner()
    res = mkdir_runner(surl, client)
    debug("mkdir returned status: %s (expl: %s)" % (status_code(res), explanation(res)))
    return res

def create_empty_remote_file(file_path):
    
    endpoint, client = get_srm_client()
    surl = get_surl(endpoint, TEST_STORAGEAREA, file_path)
    
    debug("Creating remote file: %s" % surl)
    
    ptp_runner = ptp.TestRunner()
    res = ptp_runner([surl], [], client)

    sptp_runner = sptp.TestRunner()
    while True:
        sres = sptp_runner(res, client)
        if status_code(sres) in WAITING_STATES:
            time.sleep(1)
        else:
            break
    check_success(sres, "Error in PtP for surl: %s." % surl)

    pd_runner = pd.TestRunner()
    res = pd_runner([surl], res.requestToken, client)
    check_success(res, "Error in PD for surl: " + surl)
    
    debug("File successfully created.")

def setup():
    info("Setting up file-transfer-in test.")
    
    file_name = str(uuid.uuid4());
    file_path = "%s/%s" % (TEST_DIRECTORY, file_name)
    
    create_empty_remote_file(file_path)
    
    info("file-transfer-in setup completed successfully.")
    return file_path

def cleanup(file_path):
    
    info("Cleaning up for file-transfer-in test.")
    
    endpoint, client = get_srm_client()
    surl = get_surl(endpoint, TEST_STORAGEAREA, file_path)
    res = client.srmRm([surl])
    if status_code(res) != SRM_SUCCESS:
        raise Exception("srmRm failed for %s. %s %s" % (surl, status_code(res), explanation(res)))
    
    info("file-transfer-in cleanup completed successfully.")

def do_prepare_to_get(file_path):

    endpoint, client = get_srm_client()    
    surl = get_surl(endpoint, TEST_STORAGEAREA, file_path)

    debug("do srmPtG on %s ... " % surl)
    
    ptg_runner = ptg.TestRunner()
    ptg_res = ptg_runner([surl], [TRANSFER_PROTOCOL], client)

    debug("do srmStatusPtG on %s ... " % surl)
    
    sptg_runner = sptg.TestRunner()
    counter = 0
    while True:
        res = sptg_runner(ptg_res, client)
        sc = res.returnStatus.statusCode
        counter += 1
        debug("sPtG invocation %d status code: %s" % (counter, sc))
        if sc not in WAITING_STATES:
            break
        else:
            if counter > SLEEP_THRESHOLD:
                debug("Going to sleep for %d seconds" % SLEEP_TIME)
                time.sleep(SLEEP_TIME)

    debug("SPTG result (after %d invocations): %s: %s" % (counter, res.returnStatus.statusCode, res.returnStatus.explanation))
    turl = res.getArrayOfFileStatuses().getStatusArray(0).getTransferURL()
    return (ptg_res.requestToken, turl.toString())

def do_release_file(file_path, token):

    endpoint, client = get_srm_client()    
    surl = get_surl(endpoint, TEST_STORAGEAREA, file_path)

    rf_runner = rf.TestRunner()
    rf_res = rf_runner(surl, token, client)
    
    check_success(rf_res, "Error in RF for surl %s and token %s" % (surl, token))


def file_transfer_in(target_file_path):

    (token, turl) = do_prepare_to_get(target_file_path)

    endpoint, client = get_dav_client()    

    http_get_runner = http_get.TestRunner()
    statusCode = http_get_runner(turl, client)
    check_http_success(statusCode, 200, "Error in HTTP GET")

    do_release_file(target_file_path, token)

class TestRunner:

    def __init__(self):
        
        create_remote_directory(TEST_DIRECTORY)
        self.target_file_path = setup()

    def __call__(self):
        try:
            debug("Inside call ...")
            test = Test(TestID.TXFER_IN, "StoRM file-transfer IN")
            debug("before record")
            test.record(file_transfer_in)
            debug("before transfer")
            file_transfer_in(self.target_file_path)
            debug("after transfer")
        except Exception, e:
            error("Error executing file-transfer-in: %s" % traceback.format_exc())

    def __del__(self):
        cleanup(self.target_file_path)
