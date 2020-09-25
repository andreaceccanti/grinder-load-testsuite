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
TEST_DIRECTORY  = props['rm_multi.test_directory']
TEST_NUMFILES   = int(props['rm_multi.number_of_files'])

def get_base_dir():
    
    return "%s/%s" % (TEST_STORAGEAREA, TEST_DIRECTORY)

def setup_thread_dir():

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
    
    info("rm setup completed successfully.")
    
    return test_dir

def setup_run(thread_dir):
    
    info("Setting up rm test run.")
    endpoint, client = utils.get_srm_client()

    run_test_dir = "%s/run_%s" % (thread_dir, str(grinder.getRunNumber()))
    
    info("Creating rm-test run-specific test dir: " + run_test_dir)
    run_test_dir_surl = get_surl(endpoint, run_test_dir)
    check_success(srmMkDir(client, run_test_dir_surl))
    
    surls = []
    for i in range(1, TEST_NUMFILES + 1):
        surl = get_surl(endpoint, "%s/file_%s" % (run_test_dir, i))
        surls.append(surl)
        debug("appended: %s" % surl)
    
    info("Creating rm-test test dir files ... ")
    token, response = srmPtP(client,surls,[])
    check_success(response)
    check_success(srmPd(client,surls,token))

    info("rm run setup completed successfully.")
    return surls

def get_files(surls):
    endpoint, client = utils.get_srm_client()
    for surl in surls:
        token, response = srmPtG(client, [surl], [])
        check_success(response)
        info("PTG-SYNC %s - [%s %s]" % (surl, response.returnStatus.statusCode, response.returnStatus.explanation))
        check_success(srmRf(client, surl, token))
    info("multi srmPtG+srmRf test completed.")

def ls_files(surls):
    endpoint, client = utils.get_srm_client()
    for surl in surls:
        response = srmLs(client, surl)
        info("LS %s - [%s %s]" % (surl, response.returnStatus.statusCode, response.returnStatus.explanation))
        check_success(response)
    info("multi srmLs+srmRf test completed.")

def rm_files(surls):
    endpoint, client = utils.get_srm_client()
    info("Executing rm-multi test.")
    for surl in surls:
        response = srmRm(client, [surl])
        info("Rm %s - [%s %s]" % (surl, response.returnStatus.statusCode, response.returnStatus.explanation))
        log_result_file_status(response)
        check_success(response)
    info("Rm-multi test completed.")

def get_ls_rm_files(surls):
    endpoint, client = utils.get_srm_client()
    for surl in surls:
        token, response = srmPtG(client, [surl], [])
        check_success(response)
        info("srmPtG %s - [%s %s]" % (surl, response.returnStatus.statusCode, response.returnStatus.explanation))
        response = srmRf(client, surl, token)
        check_success(response)
        info("srmRf %s - [%s %s]" % (surl, response.returnStatus.statusCode, response.returnStatus.explanation))
        response = srmLs(client, surl)
        info("srmLs %s - [%s %s]" % (surl, response.returnStatus.statusCode, response.returnStatus.explanation))
        check_success(response)
        response = srmRm(client, [surl])
        info("srmRm %s - [%s %s]" % (surl, response.returnStatus.statusCode, response.returnStatus.explanation))
        log_result_file_status(response)
        check_success(response)
    info("ptg+ls+rm multi test completed.")

def cleanup(test_dir):
    
    info("Cleaning up for rm-test.")
    endpoint, client = utils.get_srm_client()
    response = client.srmRmdir(get_surl(endpoint, test_dir), 1)
    print_srm_op("rmdir", response)
    check_success(response)
    info("rm-test cleanup completed successfully.")


class TestRunner:

    def __init__(self):
        self.thread_dir = setup_thread_dir()

    def __call__(self):
        try:
            test = Test(TestID.RM_MULTI, "StoRM srmRm multiple calls")
            test.record(get_ls_rm_files)

            surls = setup_run(self.thread_dir)
            get_ls_rm_files(surls)

        except Exception, e:
            error("Error executing rm-multi: %s" % traceback.format_exc())
    
    def __del__(self):
        
        cleanup(self.thread_dir)