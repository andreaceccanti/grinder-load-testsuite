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
import ptg
import random
import sptg
import http_get
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
BASE_FILE_PATH = props['ftin.base_file_path']

NUM_FILES=int(props['ftin.num_files'])

# Computed vars
SRM_ENDPOINT = "https://%s" % FE_HOST
SURL_PREFIX="srm://%s/%s" % (FE_HOST,BASE_FILE_PATH)

WAITING_STATES = [TStatusCode.SRM_REQUEST_QUEUED, TStatusCode.SRM_REQUEST_INPROGRESS]

# Start sleeping between sptg requests after this number
SLEEP_THRESHOLD = int(props['ftin.sleep_threshold'])

## Sleep time (seconds)
SLEEP_TIME = float(props['ftin.sleep_time'])

SRM_SUCCESS  = TStatusCode.SRM_SUCCESS


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
    info("Setting up file-transfer-in test.")
    base_dir = "%s/%s" % (SURL_PREFIX, str(uuid.uuid4()))
    info("Creating base dir: " + base_dir)

    res = client.srmMkdir(base_dir)
    check_success(res, "Error creating %s" % base_dir)
    info("Base directory succesfully created.")

    surls = []

    for i in range(0, NUM_FILES):
        f_surl = "%s/f%d" % (base_dir, i)
        if i == 0:
            info("Creating surls like this: "+ f_surl)
        surls.append(f_surl)

    res = client.srmPtP(surls,[])
    while True:
        sres = client.srmSPtP(res)
        if status_code(sres) in WAITING_STATES:
            time.sleep(1)
        else:
            break

    check_success(sres, "Error in PtP for surls (only 5 shown out of %d): %s." % (len(surls),surls[0:5]))
    res = client.srmPd(surls, res.requestToken)
    check_success(res, "Error in PD for surls: %s" % surls)
    info("file-transfer-in setup completed succesfully.")

    return base_dir,surls

def cleanup(client, base_dir):
    info("Cleaning up for file-transfer-in test.")

    res = client.srmRmdir(base_dir, True)
    if status_code(res) != SRM_SUCCESS:
        raise Exception("srmRmdir failed for %s. %s %s" %(base_dir, status_code(res), explanation(res)))
    info("file-transfer-in cleanup completed succesfully.")

def file_transfer_in(client,base_dir):
    surls=compute_surls(base_dir)
    
    protocols=[]
    protocols.append("http")
    
    #info("SURL: "+surls)
	
    ptg_runner=ptg.TestRunner()
    ptg_res=ptg_runner(surls,protocols,client)
				
    sptg_runner=sptg.TestRunner()
	
    counter=0
				
    while True:
        res=sptg_runner(ptg_res,client)
        sc=res.returnStatus.statusCode
			
        counter+=1
			
        info("sPtG invocation %d status code: %s" % (counter,sc) )
			
        if sc not in WAITING_STATES:
            break
        else:
            if counter > SLEEP_THRESHOLD:
                debug("Going to sleep for %d seconds" % SLEEP_TIME)
                time.sleep(SLEEP_TIME)
					
    info("SPTG result (after %d invocations): %s: %s" % (counter, res.returnStatus.statusCode, res.returnStatus.explanation))
		
    turls = res.getArrayOfFileStatuses().getStatusArray(0).getTransferURL()
		
    http_get_runner=http_get.TestRunner()
    res=http_get_runner(turls)

class TestRunner:								         
				
	def __call__(self):		
		try:
			test = Test(TestID.TXFER_IN, "StoRM file-transfer IN")					
			test.record(file_transfer_in)
			client = SRMClientFactory.newSRMClient(SRM_ENDPOINT,PROXY_FILE)
			
			(base_dir, surls) = setup(client)
			file_transfer_in(client, base_dir)
			cleanup(client, base_dir)
																
		except Exception, e:
			error("Error executing file-transfer-in: %s" % traceback.format_exc())
		
		
		
		