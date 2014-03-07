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
from org.italiangrid.dav.client import WebDAVClient, WebDAVClientFactory
import ptp, sptp, http_put, pd, rm
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

# Test specific variables
TEST_DIRECTORY  = props['ftout.test_directory']
TRANSFER_PROTOCOL = props['ftout.transfer_protocol']

# Start sleeping between sptg requests after this number
SLEEP_THRESHOLD = int(props['ftout.sleep_threshold'])

## Sleep time (seconds)
SLEEP_TIME      = float(props['ftout.sleep_time'])

# Get common variables:
TEST_STORAGEAREA = props['common.test_storagearea']

## Endpoints
FILETRANSFER_ENDPOINT = "https://%s:%s" % (props['common.gridhttps_host'],props['common.gridhttps_ssl_port'])
TESTCLIENT_ENDPOINT = "https://%s:%s" % (props['common.frontend_host'],props['common.frontend_port'])
SRM_ENDPOINT    = "srm://%s:%s" % (props['common.frontend_host'],props['common.frontend_port'])

WAITING_STATES  = [TStatusCode.SRM_REQUEST_QUEUED, TStatusCode.SRM_REQUEST_INPROGRESS]
SRM_SUCCESS     = TStatusCode.SRM_SUCCESS

HTTP_CLIENT     = WebDAVClientFactory.newWebDAVClient(FILETRANSFER_ENDPOINT,PROXY_FILE)

SRM_CLIENT      = SRMClientFactory.newSRMClient(TESTCLIENT_ENDPOINT,PROXY_FILE)

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

def create_test_directory_if_needed(SRM_client):
    test_dir_surl = "%s/%s/%s" % (SRM_ENDPOINT, TEST_STORAGEAREA, TEST_DIRECTORY)
    SRM_client.srmMkdir(test_dir_surl)

def create_local_file_to_upload():
    local_file_path = "/tmp/%s" % str(uuid.uuid4());
    file = open(local_file_path, "w")
    print >> file, "testo di prova"
    file.close()
    return local_file_path

def setup(client):

    info("Setting up file-transfer-out test.")
    create_test_directory_if_needed(client)
    local_file_path = create_local_file_to_upload()
    info("file-transfer-out setup completed successfully.")
    return local_file_path

def cleanup(client, target_file_name):

    info("Cleaning up for file-transfer-out test.")

    target_file_surl = "%s/%s/%s/%s" % (SRM_ENDPOINT, TEST_STORAGEAREA, TEST_DIRECTORY, target_file_name)
    rm_runner = rm.TestRunner()
    res = rm_runner(target_file_surl, client)
    if status_code(res) != SRM_SUCCESS:
        raise Exception("srmRm failed for %s. %s %s" % (target_file_surl, status_code(res), explanation(res)))

    info("file-transfer-out cleanup completed successfully.")

def do_prepare_to_put(SRM_client,surl,transfer_protocol):

    ptp_runner = ptp.TestRunner()
    ptp_res = ptp_runner([surl],[transfer_protocol],SRM_client)
    
    sptp_runner = sptp.TestRunner()
    counter=0
    while True:
        res = sptp_runner(ptp_res,SRM_client)
        sc = res.returnStatus.statusCode
        counter+=1
        info("sPtP invocation %d status code: %s" % (counter,sc) )
        if sc not in WAITING_STATES:
            break
        else:
            if counter > SLEEP_THRESHOLD:
                debug("Going to sleep for %d seconds" % SLEEP_TIME)
                time.sleep(SLEEP_TIME)

    info("SPTP result (after %d invocations): %s: %s" % (counter, res.returnStatus.statusCode, res.returnStatus.explanation))
    turl = res.getArrayOfFileStatuses().getStatusArray(0).getTransferURL()
    return (ptp_res.requestToken,turl.toString())

def do_put_done(SRM_client,surl,token):

    pd_runner=pd.TestRunner()
    pd_res = pd_runner([surl],token,SRM_client)
    check_success(pd_res, "Error in PD for surl %s and token %s" % (surl, token))

def file_transfer_out(SRM_client, HTTP_client, local_file_path, transfer_protocol):

    target_file_name = str(uuid.uuid4());
    target_file_surl = "%s/%s/%s/%s" % (SRM_ENDPOINT, TEST_STORAGEAREA, TEST_DIRECTORY, target_file_name)
    
    (token,turl) = do_prepare_to_put(SRM_client,target_file_surl,transfer_protocol)

    http_put_runner=http_put.TestRunner()
    statusCode = http_put_runner(turl,local_file_path,HTTP_client)
    check_http_success(statusCode, 204, "Error in HTTP PUT")

    do_put_done(SRM_client,target_file_surl,token)
    return target_file_name


class TestRunner:

    def __call__(self):		
        try:
            test = Test(TestID.TXFER_OUT, "StoRM file-transfer OUT")
            test.record(file_transfer_out)
            
            local_file_path = setup(SRM_CLIENT)
            target_file_name = file_transfer_out(SRM_CLIENT, HTTP_CLIENT, local_file_path, TRANSFER_PROTOCOL)
            cleanup(SRM_CLIENT, target_file_name)
            
        except Exception, e:
            error("Error executing file-transfer-out: %s" % traceback.format_exc())
