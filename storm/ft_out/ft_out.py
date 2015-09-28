from common import *
from srm import *
from exceptions import Exception
from net.grinder.script import Test
from java.io import FileInputStream
from net.grinder.script.Grinder import grinder
import http_put
import string
import time
import traceback
import uuid

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

def getUniqueName():
    
    return str(uuid.uuid4());

def check_http_success(statusCode, expected_code, error_msg):
    
    if (statusCode != expected_code):
        msg = "%s. Status code is %s instead of %s" % (error_msg, statusCode, expected_code)
        raise Exception(msg)


def get_base_dir():
    
    return "%s/%s" % (TEST_STORAGEAREA, TEST_DIRECTORY)

def setup():
    
    info("Setting up file-transfer-out test.")
    endpoint, client = utils.get_srm_client()
    
    base_dir = get_base_dir()
    remote_file_path = "%s/%s" % (base_dir, str(uuid.uuid4()))
    
    info("Creating remote test directory ... " + base_dir)
    srmMkDir(client, get_surl(endpoint, base_dir))
    
    local_file_path = create_local_file_to_upload()
    
    info("file-transfer-out setup completed successfully.")
    return local_file_path, remote_file_path

def create_local_file_to_upload():
    
    file_name = getUniqueName()
    file_path = "/tmp/%s" % file_name;
    debug("Creating local file to upload '%s'..." % file_path)
    file = open(file_path, "w")
    print >> file, "testo di prova"
    file.close()
    debug("Local file created!")
    return file_path

def cleanup(file_path):
    
    info("Cleaning up for file-transfer-out test.")
    endpoint, client = utils.get_srm_client()
    surl = get_surl(endpoint, file_path)
    check_success(client.srmRm([surl]))
    info("file-transfer-out cleanup completed successfully.")


def file_transfer_out(local_file_path, target_file_path):
    
    srm_endpoint, srm_client = utils.get_srm_client()
    dav_endpoint, dav_client = utils.get_dav_client()
    
    surl = get_surl(srm_endpoint, target_file_path)
    (token, response) = srmPtP(srm_client, [surl], [TRANSFER_PROTOCOL], True, SLEEP_THRESHOLD, SLEEP_TIME)
    check_success(response)

    http_put_runner = http_put.TestRunner()
    statusCode = http_put_runner(get_turl(response), local_file_path, dav_client)
    check_http_success(statusCode, 204, "Error in HTTP PUT")

    check_success(srmPd(srm_client, [surl], token))

class TestRunner:

    def __init__(self):
        
        (self.local_file_path, self.target_file_path) = setup()

    def __call__(self):
        
        try:
            test = Test(TestID.TXFER_OUT, "StoRM file-transfer OUT")
            test.record(file_transfer_out)
            file_transfer_out(self.local_file_path, self.target_file_path)
            cleanup(self.target_file_path)
        except Exception, e:
            error("Error executing file-transfer-out: %s" % traceback.format_exc())
