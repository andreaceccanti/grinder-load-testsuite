from common import *
from srm import *
from exceptions import Exception
from net.grinder.script import Test
from net.grinder.script.Grinder import grinder
import random
import time
import traceback
import uuid

error          = grinder.logger.error
info           = grinder.logger.info
debug          = grinder.logger.debug
props          = grinder.properties

utils          = Utils(grinder.properties)

# Common variables:
TEST_STORAGEAREA = props['common.test_storagearea']

# Test specific variables
TEST_DIRECTORY = props["ptg_sync.test_directory"]

## Start sleeping between sptg requests after this number
SLEEP_THRESHOLD = int(props["ptg_sync.sleep_threshold"])

## Sleep time (seconds)
SLEEP_TIME = float(props["ptg_sync.sleep_time"])

## Perform an srmPing before running the test to rule out the handshake time from the status
DO_HANDSHAKE = bool(props["ptg_sync.do_handshake"])

## Number of files created in the ptg directory
NUM_FILES = int(props["ptg_sync.num_files"])

def get_base_dir():
    
    return "%s/%s" % (TEST_STORAGEAREA, TEST_DIRECTORY)

def setup():
    
    info("Setting up ptg-sync test.")

    endpoint, client = utils.get_srm_client()
    
    dir_name = str(uuid.uuid4())
    base_dir = get_base_dir()
    test_dir = "%s/%s" % (base_dir, dir_name)
    
    info("Creating remote test directory ... " + base_dir)
    srmMkDir(client, get_surl(endpoint, base_dir))
    
    info("Creating ptg-sync specific test dir: " + test_dir)
    test_dir_surl = get_surl(endpoint, test_dir)
    check_success(srmMkDir(client, test_dir_surl))
    
    info("Creating file surls ... ")
    surls = []
    for i in range(0, NUM_FILES):
        f_surl = get_surl(endpoint, "%s/f%s" % (test_dir, i))
        surls.append(f_surl)
        debug("Added SURL: %s" % f_surl)

    token, response = srmPtP(client,surls,[])
    check_success(response)
    check_success(srmPd(client,surls,token))
    
    info("ptg-sync setup completed successfully.")

    return test_dir,surls

def cleanup(test_dir):
    
    info("Cleaning up for ptg-sync test.")
    endpoint, client = utils.get_srm_client()
    check_success(client.srmRmdir(get_surl(endpoint, test_dir), 1))
    info("ptg-sync cleanup completed succesfully.")

def ptg_sync(surl):
    
    endpoint, client = utils.get_srm_client()
    token, response = srmPtG(client, [surl], [])
    check_success(response)
    info("PTG-SYNC %s - [%s %s]" % (surl, response.returnStatus.statusCode, response.returnStatus.explanation))
    check_success(srmRf(client, surl, token))

class TestRunner:
    
    def __init__(self):

        (self.test_dir, self.surls) = setup()
    
    def __call__(self):
        
        try:
            test = Test(TestID.PTG_TEST, "StoRM Sync PTG test")
            test.record(ptg_sync)
            
            if DO_HANDSHAKE:
                endpoint, client = utils.get_srm_client()
                debug("Ping %s ..." % endpoint)
                client.srmPing()
            
            ptg_sync(random.choice(self.surls))

        except Exception:
            error("Error executing ptg-sync: %s" % traceback.format_exc())
    
    def __del__(self):
        
        cleanup(self.test_dir)
