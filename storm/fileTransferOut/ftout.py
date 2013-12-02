from common import TestID, load_common_properties
from eu.emi.security.authn.x509.impl import PEMCredential
from exceptions import Exception
from gov.lbl.srm.StorageResourceManager import TStatusCode
from jarray import array
from java.io import FileInputStream
from javax.net.ssl import X509ExtendedKeyManager
from net.grinder.plugin.http import HTTPRequest
from net.grinder.script import Test
from net.grinder.script.Grinder import grinder
from org.italiangrid.srm.client import SRMClient, SRMClientFactory
import ptp
import random
import sptp
import http_put
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


PROXY_FILE     = props['client.proxy']
FE_HOST        = props['storm.host']
BASE_FILE_PATH = props['ftout.base_file_path']

NUM_FILES=int(props['ftout.num_files'])

# Computed vars
SRM_ENDPOINT = "https://%s" % FE_HOST
SURL_PREFIX="srm://%s/%s" % (FE_HOST,BASE_FILE_PATH)

WAITING_STATES = [TStatusCode.SRM_REQUEST_QUEUED, TStatusCode.SRM_REQUEST_INPROGRESS]

# Start sleeping between sptg requests after this number
SLEEP_THRESHOLD = int(props['ftout.sleep_threshold'])

## Sleep time (seconds)
SLEEP_TIME = float(props['ftout.sleep_time'])

SRM_SUCCESS  = TStatusCode.SRM_SUCCESS

NUM_BYTES = int(props['ftout.num_bytes_transferred'])

def status_code(resp):
    return resp.returnStatus.statusCode

def explanation(resp):
    return resp.returnStatus.explanation

def check_success(res, msg):
    if status_code(res) != SRM_SUCCESS:
        error_msg = "%s. %s (expl: %s)" % (msg, status_code(res), explanation(res))
        raise Exception(error_msg)

def compute_surls(base_dir):
    random_index = random.randint(0,NUM_FILES-1)
    surl = "%s/f%d" % (base_dir,random_index)
    return [surl]
   
def setup(client):
    info("Setting up file-transfer-out test.")
    base_dir = "%s/%s" % (SURL_PREFIX, str(uuid.uuid4()))
    info("Creating base dir: " + base_dir)

    res = client.srmMkdir(base_dir)
    check_success(res, "Error creating %s" % base_dir)
    info("Base directory succesfully created.")

    return base_dir

def cleanup(client, base_dir):
    info("Cleaning up for file-transfer-out test.")

    res = client.srmRmdir(base_dir, True)
    if status_code(res) != SRM_SUCCESS:
        raise Exception("srmRmdir failed for %s. %s %s" %(base_dir, status_code(res), explanation(res)))
    info("file-transfer-out cleanup completed succesfully.")

def file_transfer_out(client,base_dir):
    surls=compute_surls(base_dir)
    
    protocols=[]
    protocols.append("http")
	    	
    ptp_runner=ptp.TestRunner()
    ptp_res=ptp_runner(surls,protocols,client)
                
    sptp_runner=sptp.TestRunner()
    
    counter=0
            
    while True:
        res=sptp_runner(ptp_res,client)
        sc=res.returnStatus.statusCode
            
        counter+=1
            
        info("sPtP invocation %d status code: %s" % (counter,sc) )
            
        if sc not in WAITING_STATES:
            break
        else:
            if counter > SLEEP_THRESHOLD:
                debug("Going to sleep for %d seconds" % SLEEP_TIME)
                time.sleep(SLEEP_TIME)
                    
    info("SPTP result (after %d invocations): %s: %s" % (counter, res.returnStatus.statusCode, res.returnStatus.explanation))
				                                            
    turls = res.getArrayOfFileStatuses().getStatusArray(0).getTransferURL()
        
    http_put_runner=http_put.TestRunner()
    put_res=http_put_runner(turls,NUM_BYTES)  
                                                                    
    res = client.srmPd(surls, ptp_res.requestToken)
    check_success(res, "Error in PD for surls: %s" % surls)    
        
    

class TestRunner:								         
				
	def __call__(self):		
		try:
			test = Test(TestID.TXFER_IN, "StoRM file-transfer OUT")					
			test.record(file_transfer_out)
			client = SRMClientFactory.newSRMClient(SRM_ENDPOINT,PROXY_FILE)
			
			base_dir = setup(client)
			file_transfer_out(client, base_dir)
			cleanup(client, base_dir)
																
		except Exception, e:
			error("Error executing file-transfer-out: %s" % traceback.format_exc())
		
		
		
		