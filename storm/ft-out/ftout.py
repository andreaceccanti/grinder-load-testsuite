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
import mkdir, ptp, sptp, http_put, pd, rm
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
FRONTEND_ENDPOINT = "https://%s:%s" % (props['common.frontend_host'],props['common.frontend_port'])
SRM_ENDPOINT    = "srm://%s:%s" % (props['common.frontend_host'],props['common.frontend_port'])

WAITING_STATES  = [TStatusCode.SRM_REQUEST_QUEUED, TStatusCode.SRM_REQUEST_INPROGRESS]
SRM_SUCCESS     = TStatusCode.SRM_SUCCESS

# Computed variables:
TEST_DIRECTORY_SURL = "%s/%s/%s" % (SRM_ENDPOINT, TEST_STORAGEAREA, TEST_DIRECTORY)

def status_code(resp):
    return resp.returnStatus.statusCode

def explanation(resp):
    return resp.returnStatus.explanation

def getUniqueName():
    return str(uuid.uuid4());


def check_success(res, msg):
    if status_code(res) != SRM_SUCCESS:
        error_msg = "%s. %s (expl: %s)" % (msg, status_code(res), explanation(res))
        raise Exception(error_msg)

def check_http_success(statusCode, expected_code, error_msg):
    if (statusCode != expected_code):
        msg = "%s. Status code is %s instead of %s" % (error_msg, statusCode, expected_code)
        raise Exception(msg)

def create_test_directory_if_needed(client):
    debug("Creating test directory '%s'..." % TEST_DIRECTORY_SURL)
    mkdir_runner = mkdir.TestRunner()
    res = mkdir_runner(TEST_DIRECTORY_SURL, client)
    debug("Returned status: %s %s", (status_code(res), explanation(res)))

def create_local_file_to_upload(local_file_name):
    local_file_path = "/tmp/%s" % local_file_name;
    debug("Creating local test file to upload '%s'..." % local_file_path)
    file = open(local_file_path, "w")
    print >> file, "testo di prova"
    file.close()
    debug("Local file created!")
    return local_file_path

def setup(client):
    debug("Setting up file-transfer-out test.")
    create_test_directory_if_needed(client)
    file_name = getUniqueName()
    local_file_path = create_local_file_to_upload(file_name)
    target_file_surl = "%s/%s/%s/%s" % (SRM_ENDPOINT, TEST_STORAGEAREA, TEST_DIRECTORY, file_name)
    debug("file-transfer-out setup completed successfully.")
    return (local_file_path,target_file_surl)

def cleanup(client, target_file_surl):
    debug("Removing '%s'..." % target_file_surl)
    rm_runner = rm.TestRunner()
    res = rm_runner([target_file_surl], client)
    #res = client.srmRm([target_file_surl])
    if status_code(res) != SRM_SUCCESS:
        raise Exception("srmRm failed for %s. %s %s" % (target_file_surl, status_code(res), explanation(res)))
    debug("Returned status: %s %s", (status_code(res), explanation(res)))

def do_prepare_to_put(SRM_client, surl, transfer_protocol):
    debug("Doing a PrepareToPut on '%s' with transfer protocol '%s'..." % (surl, transfer_protocol))
    ptp_runner = ptp.TestRunner()
    ptp_res = ptp_runner([surl],[transfer_protocol],SRM_client)
    debug("Got token: %s" % ptp_res.requestToken)
    sptp_runner = sptp.TestRunner()
    counter=0
    while True:
        res = sptp_runner(ptp_res,SRM_client)
        sc = res.returnStatus.statusCode
        counter+=1
        debug("sPtP invocation %d status code: %s" % (counter,sc) )
        if sc not in WAITING_STATES:
            break
        else:
            if counter > SLEEP_THRESHOLD:
                debug("Going to sleep for %d seconds" % SLEEP_TIME)
                time.sleep(SLEEP_TIME)
    debug("SPTP result (after %d invocations): %s: %s" % (counter, status_code(res), explanation(res)))
    turl = res.getArrayOfFileStatuses().getStatusArray(0).getTransferURL()
    debug("Returned %s, %s and TURL %s" % (status_code(res), explanation(res), turl))
    return (ptp_res.requestToken, turl.toString())

def do_put_done(SRM_client, surl, token):
    debug("Doing a PutDone on '%s' with token '%s'..." % (surl, token))
    pd_runner=pd.TestRunner()
    res = pd_runner([surl], token, SRM_client)
    debug("Returned status is %s, %s" % (status_code(res), explanation(res)))
    check_success(res, "Error in PD for surl %s and token %s" % (surl, token))

def file_transfer_out(SRM_client, HTTP_client, local_file_path, target_file_surl, transfer_protocol):
    (token,turl) = do_prepare_to_put(SRM_client,target_file_surl,transfer_protocol)
    http_put_runner = http_put.TestRunner()
    statusCode = http_put_runner(turl,local_file_path,HTTP_client)
    check_http_success(statusCode, 204, "Error in HTTP PUT")
    do_put_done(SRM_client,target_file_surl,token)


class TestRunner:

    def __init__(self):
        self.SRMclient = SRMClientFactory.newSRMClient(FRONTEND_ENDPOINT,PROXY_FILE)
        self.HTTPclient = WebDAVClientFactory.newWebDAVClient(FILETRANSFER_ENDPOINT,PROXY_FILE)
        self.transfer_protocol = TRANSFER_PROTOCOL
        (self.local_file_path, self.target_file_surl) = setup(self.SRMclient)

    def __call__(self):
        try:
            test = Test(TestID.TXFER_OUT, "StoRM file-transfer OUT")
            test.record(file_transfer_out)
            file_transfer_out(self.SRMclient, self.HTTPclient, self.local_file_path, self.target_file_surl, self.transfer_protocol)
            cleanup(self.SRMclient, self.target_file_surl)
        except Exception, e:
            error("Error executing file-transfer-out: %s" % traceback.format_exc())
