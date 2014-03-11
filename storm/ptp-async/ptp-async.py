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
import ptp, sptp, pd, rm
import random
import string
import time
import traceback
import uuid

## This loads the base properties inside grinder properties
## Should be left at the top of the script execution
load_common_properties()

error          = grinder.logger.error
info           = grinder.logger.info
debug          = grinder.logger.debug

props          = grinder.properties


# Proxy authorized to write on SRM/WEBDAV endpoints
PROXY_FILE      = get_proxy_file_path()

# Common variables:
TEST_STORAGEAREA = props['common.test_storagearea']

## Endpoints
FILETRANSFER_ENDPOINT = "https://%s:%s" % (props['common.gridhttps_host'],props['common.gridhttps_ssl_port'])
FRONTEND_ENDPOINT = "https://%s:%s" % (props['common.frontend_host'],props['common.frontend_port'])
SRM_ENDPOINT    = "srm://%s:%s" % (props['common.frontend_host'],props['common.frontend_port'])

# Test specific variables
TEST_DIRECTORY  = props['ptp-async.test_directory']
SLEEP_THRESHOLD = int(props['ptp-async.sleep_threshold'])
SLEEP_TIME      = float(props['ptp-async.sleep_time'])

# Init other global variables
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

def create_test_directory_if_needed(client):
    test_dir_surl = "%s/%s/%s" % (SRM_ENDPOINT, TEST_STORAGEAREA, TEST_DIRECTORY)
    client.srmMkdir(test_dir_surl)

def setup(client):
    info("Setting up ptp-async test.")
    create_test_directory_if_needed(client)
    info("ptp-async setup completed successfully.")

def do_prepare_to_put(client,surl):
    ptp_runner = ptp.TestRunner()
    ptp_res = ptp_runner([surl],[],client)
    sptp_runner = sptp.TestRunner()
    counter=0
    while True:
        res = sptp_runner(ptp_res,client)
        sc = res.returnStatus.statusCode
        counter+=1
        info("sPtP invocation %d status code: %s" % (counter,sc) )
        if sc not in WAITING_STATES:
            break
        else:
            if counter > SLEEP_THRESHOLD:
                debug("Going to sleep for %d seconds" % SLEEP_TIME)
                time.sleep(SLEEP_TIME)
    info("sPTP result (after %d invocations): %s: %s" % (counter, res.returnStatus.statusCode, res.returnStatus.explanation))
    turl = res.getArrayOfFileStatuses().getStatusArray(0).getTransferURL()
    return (ptp_res.requestToken,turl.toString())

def do_put_done(client,surl,token):
    pd_runner=pd.TestRunner()
    pd_res = pd_runner([surl],token,client)
    check_success(pd_res, "Error in PD for surl %s and token %s" % (surl, token))

def ptp_async(client):
    target_file_name = str(uuid.uuid4());
    target_file_surl = "%s/%s/%s/%s" % (SRM_ENDPOINT, TEST_STORAGEAREA, TEST_DIRECTORY, target_file_name)
    (token,turl) = do_prepare_to_put(client,target_file_surl)
    do_put_done(client,target_file_surl,token)
    return target_file_name

def cleanup(client, target_file_name):
    info("Cleaning up for ptp-async test.")
    target_file_surl = "%s/%s/%s/%s" % (SRM_ENDPOINT, TEST_STORAGEAREA, TEST_DIRECTORY, target_file_name)
    rm_runner = rm.TestRunner()
    res = rm_runner(target_file_surl, client)
    if status_code(res) != SRM_SUCCESS:
        raise Exception("RM failed for %s. %s %s" % (target_file_surl, status_code(res), explanation(res)))
    debug("Cleaned up %s" % target_file_surl)

class TestRunner:
    def __call__(self):
        try:
            test = Test(TestID.PTP_ASYNC_PD, "StoRM PTP Async test")
            test.record(ptp_async)

            setup(SRM_CLIENT)
            file_name = ptp_async(SRM_CLIENT)
            cleanup(SRM_CLIENT, file_name)

        except Exception, e:
            error("Error executing ptp-async: %s" % traceback.format_exc())
            raise
