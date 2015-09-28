from common import *
from srm import *
from exceptions import Exception
from jarray import array
from java.io import FileInputStream
from net.grinder.script import Test
from net.grinder.script.Grinder import grinder
import random
import string
import time
import traceback
import uuid

error          = grinder.logger.error
info           = grinder.logger.info
debug          = grinder.logger.debug

props          = grinder.properties

utils           = Utils(grinder.properties)

# Common variables:
TEST_STORAGEAREA = props['common.test_storagearea']

# Test specific variables
TEST_DIRECTORY  = props['ptp_test.test_directory']
SLEEP_THRESHOLD = int(props['ptp_test.sleep_threshold'])
SLEEP_TIME      = float(props['ptp_test.sleep_time'])

def get_base_dir():
    
    return "%s/%s" % (TEST_STORAGEAREA, TEST_DIRECTORY)

def setup():

    info("Setup ptp test ...")
    endpoint, client = utils.get_srm_client()
    
    dir_name = str(uuid.uuid4())
    base_dir = get_base_dir()
    test_dir = "%s/%s" % (base_dir, dir_name)
    
    info("Creating remote test directory ... " + base_dir)
    srmMkDir(client, get_surl(endpoint, base_dir))
    
    info("Creating ptp specific test dir: " + test_dir)
    test_dir_surl = get_surl(endpoint, test_dir)
    check_success(srmMkDir(client, test_dir_surl))

    info("ptp setup completed successfully.")
    return test_dir

def ptp_test(file_path):

    endpoint, client = utils.get_srm_client()
    surl = get_surl(endpoint, file_path)
    token, response = srmPtP(client, [surl], [])
    check_success(response)
    info("PTP-SYNC %s - [%s %s]" % (surl, response.returnStatus.statusCode, response.returnStatus.explanation))
    check_success(srmPd(client, [surl], token))

def cleanup(file_path):

    debug("Cleaning up for ptp-async test.")
    endpoint, client = utils.get_srm_client()
    surl = get_surl(endpoint, file_path)
    response = srmRm(client, [surl])
    info("Rm %s - [%s %s]" % (surl, response.returnStatus.statusCode, response.returnStatus.explanation))
    debug("Cleaned up ptp-sync.")

class TestRunner:

    def __init__(self):

        self.test_dir = setup()

    def __call__(self):

        try:

            test = Test(TestID.PTP_TEST, "StoRM PTP Sync test")
            test.record(ptp_test)

            target_file_name = "%s/%s" % (self.test_dir, str(uuid.uuid4()))
            ptp_test(target_file_name)
            cleanup(target_file_name)

        except Exception, e:
            error("Error executing ptp-async: %s" % traceback.format_exc())
            raise
