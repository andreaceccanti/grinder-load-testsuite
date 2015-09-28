from common import *
from srm import *
from exceptions import Exception
from net.grinder.script import Test
from net.grinder.script.Grinder import grinder
import http_get
import string
import time
import traceback
import uuid

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

def check_http_success(statusCode, expected_code, error_msg):
    
    if (statusCode != expected_code):
        msg = "%s. Status code is %s instead of %s" % (error_msg, statusCode, expected_code)
        raise Exception(msg)

def get_base_dir():
    
    return "%s/%s" % (TEST_STORAGEAREA, TEST_DIRECTORY)

def setup():
    
    info("Setting up file-transfer-in test.")
    endpoint, client = utils.get_srm_client()
    
    base_dir = get_base_dir()
    file_path = "%s/%s" % (base_dir, str(uuid.uuid4()))
    
    info("Creating remote test directory ... " + base_dir)
    srmMkDir(client, get_surl(endpoint, base_dir))
    
    surl = get_surl(endpoint, file_path)
    
    token, response = srmPtP(client, [surl], [])
    check_success(response)
    check_success(srmPd(client, [surl], token))
    
    info("file-transfer-in setup completed successfully.")
    return file_path

def cleanup(file_path):
    
    info("Cleaning up for file-transfer-in test.")
    endpoint, client = utils.get_srm_client()
    surl = get_surl(endpoint, file_path)
    check_success(client.srmRm([surl]))
    info("file-transfer-in cleanup completed successfully.")

def file_transfer_in(target_file_path):

    srm_endpoint, srm_client = utils.get_srm_client()
    dav_endpoint, dav_client = utils.get_dav_client()
    
    surl = get_surl(srm_endpoint, target_file_path)
    (token, response) = srmPtG(srm_client, [surl], [TRANSFER_PROTOCOL], True, SLEEP_THRESHOLD, SLEEP_TIME)
    check_success(response)

    http_get_runner = http_get.TestRunner()
    statusCode = http_get_runner(get_turl(response), dav_client)
    check_http_success(statusCode, 200, "Error in HTTP GET")

    check_success(srmRf(srm_client, surl, token))

class TestRunner:

    def __init__(self):
        
        self.target_file_path = setup()

    def __call__(self):

        try:

            test = Test(TestID.TXFER_IN, "StoRM file-transfer IN")
            test.record(file_transfer_in)
            file_transfer_in(self.target_file_path)

        except Exception, e:
            error("Error executing file-transfer-in: %s" % traceback.format_exc())

    def __del__(self):

        cleanup(self.target_file_path)
