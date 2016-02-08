from common import *
from srm import *
from exceptions import Exception
from jarray import array
from net.grinder.script import Test
from net.grinder.script.Grinder import grinder
import http_put
import random
import time
import traceback
import uuid

# Test: create width x height elements, save surls and ls one element random each run

error          = grinder.logger.error
info           = grinder.logger.info
debug          = grinder.logger.debug

props          = grinder.properties

utils          = Utils(grinder.properties)

# Get common variables:
TEST_STORAGEAREA = props['common.test_storagearea']

# Test specific variables
TEST_DIRECTORY  = props['atlas_nested.directory']
NESTING_LEVELS   = int(props['atlas_nested.nesting_levels'])
FILE_SIZE_IN_BYTES = int(props['atlas_nested.file_size_in_bytes'])

TRANSFER_PROTOCOL = props['atlas_nested.transfer_protocol']
SLEEP_THRESHOLD = int(props['atlas_nested.sleep_threshold'])
SLEEP_TIME = float(props['atlas_nested.sleep_time'])

def get_base_dir():
    
    return "%s/%s" % (TEST_STORAGEAREA, TEST_DIRECTORY)

def get_random_dir_name():
    
    return str(uuid.uuid4())[:2]

def check_http_success(statusCode, expected_code, error_msg):
    
    if (statusCode != expected_code):
        msg = "%s. Status code is %s instead of %s" % (error_msg, statusCode, expected_code)
        raise Exception(msg)

def setup():
    
    info("Setting up atlas_workflow test.")
    srm_endpoint, srm_client = utils.get_srm_client()
    dav_endpoint, dav_client = utils.get_dav_client()
    
    test_dir = get_base_dir()
    info("Creating remote test directory ... " + test_dir)
    srmMkDir(srm_client, get_surl(srm_endpoint, test_dir))
    
    for i in range(1, NESTING_LEVELS + 1):
        dir_name = get_random_dir_name()
        test_dir = "%s/%s" % (test_dir, dir_name)
        info("Creating remote test directory ... " + test_dir)
        srmMkDir(srm_client, get_surl(srm_endpoint, test_dir))
    
    info("Creating local file to upload ...")
    file_name = str(uuid.uuid4())
    local_file_path = "/tmp/%s" % file_name;
    file = open(local_file_path, "w")
    for i in range(1, FILE_SIZE_IN_BYTES + 1):
        print >> file, "@"
    file.close()

    info("Upload local file to: " + test_dir)
    surl = get_surl(srm_endpoint, "%s/%s" % (test_dir, file_name))
    
    (token, response) = srmPtP(srm_client, [surl], [TRANSFER_PROTOCOL], True, SLEEP_THRESHOLD, SLEEP_TIME)
    check_success(response)

    http_put_runner = http_put.TestRunner()
    statusCode = http_put_runner(get_turl(response), local_file_path, dav_client)
    check_http_success(statusCode, 204, "Error in HTTP PUT")

    check_success(srmPd(srm_client, [surl], token))

    info("Atlas workflow setup completed successfully.")
    return local_file_path, surl

def atlas_test(surl):
    
    endpoint, client = utils.get_srm_client()
    response = srmLs(client, surl)
    info("LS %s - [%s %s]" % (surl, response.returnStatus.statusCode, response.returnStatus.explanation))
    check_success(response)
    token, response = srmPtG(client, [surl], [])
    check_success(response)
    info("PTG-SYNC %s - [%s %s]" % (surl, response.returnStatus.statusCode, response.returnStatus.explanation))
    check_success(srmRf(client, surl, token))

def cleanup(surl, local_file_path):
    
    info("Cleaning up for atlas-test.")
    os.remove(local_file_path)
    endpoint, client = utils.get_srm_client()
    check_success(client.srmRm([surl]))
    info("atlas-test cleanup completed successfully.")

class TestRunner:

    def __init__(self):
        
        (self.local_file_path, self.surl) = setup()

    def __call__(self):
        
        try:

            test = Test(TestID.ATLAS_TEST, "StoRM Atlas workflow test")
            test.record(atlas_test)
            atlas_test(self.surl)

        except Exception, e:

            error("Error executing ls test: %s" % traceback.format_exc())
            raise
    
    def __del__(self):
        
        cleanup(self.surl, self.local_file_path)