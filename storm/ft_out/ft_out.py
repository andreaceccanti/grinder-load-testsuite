from common import *
from exceptions import Exception
from gov.lbl.srm.StorageResourceManager import TStatusCode
from jarray import array
from java.io import FileInputStream
from net.grinder.script import Test
from net.grinder.script.Grinder import grinder
import mkdir, ptp, sptp, http_put, pd, rm
import string
import time
import traceback
import uuid
import os

error          = grinder.logger.error
info           = grinder.logger.info
debug          = grinder.logger.debug

props          = grinder.properties

utils = Utils(grinder.properties)

# Common variables:
TEST_STORAGEAREA = props['common.test_storagearea']

# Test specific variables
TEST_DIRECTORY = props['ft_out.test_directory']
TRANSFER_PROTOCOL = props['ft_out.transfer_protocol']
SLEEP_THRESHOLD = int(props['ft_out.sleep_threshold'])
SLEEP_TIME = float(props['ft_out.sleep_time'])

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

def create_remote_directory(dir_path):
    
    endpoint, client = get_srm_client()
    surl = get_surl(endpoint, TEST_STORAGEAREA, dir_path)
    mkdir_runner = mkdir.TestRunner()
    res = mkdir_runner(surl, client)
    debug("mkdir returned status: %s (expl: %s)" % (status_code(res), explanation(res)))
    return res

def remove_remote_file(file_path):
    
    endpoint, client = get_srm_client()
    surl = get_surl(endpoint, TEST_STORAGEAREA, file_path)
    rm_runner = rm.TestRunner()
    res = rm_runner([surl], client)
    check_success(res, "Error on removing %s" % file_path)

def create_local_file_to_upload():
    
    file_name = getUniqueName()
    file_path = "/tmp/%s" % file_name;
    debug("Creating local file to upload '%s'..." % file_path)
    file = open(file_path, "w")
    print >> file, "testo di prova"
    file.close()
    debug("Local file created!")
    return file_path

def setup():
    
    debug("Setting up file-transfer-out test.")
    local_file_path = create_local_file_to_upload()
    create_remote_directory(TEST_DIRECTORY)
    debug("file-transfer-out setup completed successfully.")
    return local_file_path

def cleanup(file_path):
    
    debug("Removing '%s'..." % file_path)
    remove_remote_file(file_path)
    debug("File removed")

def do_prepare_to_put(client, surl, t_protocol):
    
    debug("Doing a PrepareToPut on '%s' with transfer protocol '%s'..." % (surl, t_protocol))
    ptp_runner = ptp.TestRunner()
    ptp_res = ptp_runner([surl],[t_protocol],client)
    debug("Got token: %s" % ptp_res.requestToken)
    sptp_runner = sptp.TestRunner()
    counter=0
    while True:
        res = sptp_runner(ptp_res,client)
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

def do_put_done(client, surl, token):
    
    debug("Doing a PutDone on '%s' with token '%s'..." % (surl, token))
    pd_runner=pd.TestRunner()
    res = pd_runner([surl], token, client)
    debug("Returned status is %s, %s" % (status_code(res), explanation(res)))
    check_success(res, "Error in PD for surl %s and token %s" % (surl, token))

def file_transfer_out(local_file_path, target_file_path):
    
    endpoint_srm, srm_client = get_srm_client()
    endpoint_dav, dav_client = get_dav_client()
    
    surl = get_surl(endpoint_srm, TEST_STORAGEAREA, target_file_path)
    
    (token,turl) = do_prepare_to_put(srm_client, surl, TRANSFER_PROTOCOL)
    
    http_put_runner = http_put.TestRunner()
    statusCode = http_put_runner(turl, local_file_path, dav_client)
    check_http_success(statusCode, 204, "Error in HTTP PUT")
    
    do_put_done(srm_client, surl, token)

class TestRunner:

    def __init__(self):
        
        self.local_file_path = setup()
        self.target_file_path = "%s/%s" % (TEST_DIRECTORY, getUniqueName())

    def __call__(self):
        
        try:
            test = Test(TestID.TXFER_OUT, "StoRM file-transfer OUT")
            test.record(file_transfer_out)
            file_transfer_out(self.local_file_path, self.target_file_path)
            cleanup(self.target_file_path)
        except Exception, e:
            error("Error executing file-transfer-out: %s" % traceback.format_exc())
