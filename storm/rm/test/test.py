from eu.emi.security.authn.x509.impl import PEMCredential
from jarray import array
from java.io import FileInputStream
from javax.net.ssl import X509ExtendedKeyManager
from net.grinder.plugin.http import HTTPRequest
from net.grinder.script import Test
from net.grinder.script.Grinder import grinder
from org.italiangrid.srm.client import SRMClient, SRMClientFactory
import random

## alias for grinder.properties
props = grinder.properties

## alias for grinder info logger
log = grinder.logger.info

## test parameters as fetched from grinder.properties
PROXY_FILE = props['storm.rm.proxy']
SRM_HOST = props['storm.host']
SRM_ENDPOINT = "https://%s" % SRM_HOST
BASE_FILE_PATH=props['storm.rm.base_file_path']
NUM_FILES=int(props['storm.rm.num_files'])
NUM_SURLS=int(props['storm.rm.num_surls'])
MAX_WAITING_TIME_IN_MSEC=int(props['storm.rm.max_waiting_time_in_msec'])

SURL_PREFIX="srm://%s/%s" % (SRM_HOST, BASE_FILE_PATH)

## this currently unused method is how you should initialize
## the Grinder SSL module when you want to use a proxy for HTTP requests
def setup_keymanager():
    cred = PEMCredential(FileInputStream(PROXY_FILE), None)
    key_managers = array((cred.getKeyManager(),), X509ExtendedKeyManager)
    grinder.SSLControl.setKeyManagers(key_managers)

def log_properties():
    log("PtG test configuration")
    for k in sorted(props.keys()):
        log("%s : %s" %(k, props[k])) 
            
class TestRunner:    

    def __init__(self):
        self.files = []
        for i in range(1, NUM_FILES + 1):
          self.files.append("f" + str(i))

    def __call__(self):        

       # stop thread if there's not files to delete anymore
        if not self.files:
            grinder.stopThisWorkerThread()

        test = Test(8, "StoRM srmRm")
        
        client = SRMClientFactory.newSRMClient(SRM_ENDPOINT, PROXY_FILE)
        
        surls = []
        for i in range(0, NUM_SURLS):
            surls.append(SURL_PREFIX + "/d" + str(grinder.getThreadNumber() + 1) + "/" + self.files.pop())
        
        test.record(client)
        
        res = client.srmRm(surls)
        
        log("Remove result: %s: %s" % (res.returnStatus.statusCode, 
                                    res.returnStatus.explanation))
        
        statuses = res.getArrayOfFileStatuses().getStatusArray() 
        
        for s in statuses:
            log("%s -> %s" %(s.getSurl(),
                             s.getStatus().getStatusCode()))
