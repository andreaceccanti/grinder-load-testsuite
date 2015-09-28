from common import *
from srm import *
from jarray import array
from net.grinder.script import Test
from net.grinder.script.Grinder import grinder
import traceback
import time
import random
import uuid

error           = grinder.logger.error
info            = grinder.logger.info
debug           = grinder.logger.debug

props           = grinder.properties

utils           = Utils(grinder.properties)

# Get common variables:
TEST_STORAGEAREA = props['common.test_storagearea']

# Test specific variables
TEST_DIRECTORY  = props['rm_test.directory']
TEST_NUMFILES   = int(props['rm_test.number_of_files'])

def get_base_dir():
    
    return "%s/%s" % (TEST_STORAGEAREA, TEST_DIRECTORY)

def setup():
    
    info("Setting up rm test.")
    endpoint, client = utils.get_srm_client()
    
    dir_name = str(uuid.uuid4())
    base_dir = get_base_dir()
    test_dir = "%s/%s" % (base_dir, dir_name)
    
    info("Creating remote test directory ... " + base_dir)
    srmMkDir(client, get_surl(endpoint, base_dir))
    
    info("Creating rm-test specific test dir: " + test_dir)
    test_dir_surl = get_surl(endpoint, test_dir)
    check_success(srmMkDir(client, test_dir_surl))
    
    surls = []
    for i in range(1, TEST_NUMFILES + 1):
        surl = get_surl(endpoint, "%s/file_%s" % (test_dir, i))
        surls.append(surl)
        debug("appended: %s" % surl)
    
    info("Creating rm-test test dir files ... ")
    token, response = srmPtP(client,surls,[])
    check_success(response)
    check_success(srmPd(client,surls,token))

    info("rm setup completed successfully.")
    return test_dir, surls

def rm_files(surls):
    
    endpoint, client = utils.get_srm_client()
    response = srmRm(client, surls)
    info("Rm %s - [%s %s]" % (surls, response.returnStatus.statusCode, response.returnStatus.explanation))
    log_result_file_status(response)
    check_success(response)

def cleanup(test_dir):
    
    info("Cleaning up for rm-test.")
    endpoint, client = utils.get_srm_client()
    check_success(client.srmRmdir(get_surl(endpoint, test_dir), 1))
    info("rm-test cleanup completed successfully.")


class TestRunner:

    def __call__(self):
        try:
            test = Test(TestID.RM_TEST, "StoRM srmRm files")
            test.record(rm_files)

            (self.test_dir, self.surls) = setup()
            rm_files(self.surls)

        except Exception, e:
            error("Error executing rm-files: %s" % traceback.format_exc())
    
    def __del__(self):
        
        cleanup(self.test_dir)