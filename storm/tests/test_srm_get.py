from eu.emi.security.authn.x509.impl import PEMCredential
from jarray import array
from java.io import FileInputStream
from javax.net.ssl import X509ExtendedKeyManager
from net.grinder.plugin.http import HTTPRequest
from net.grinder.script import Test
from net.grinder.script.Grinder import grinder
from org.italiangrid.srm.client import SRMClient, SRMClientFactory
import random

## Alias for grinder.properties
props = grinder.properties

## Alias for grinder info logger
log = grinder.logger.info

## Test parameters as fetched from grinder.properties
PROXY_FILE = props['storm.ptg.proxy']
SRM_HOST = props['storm.host']
SRM_ENDPOINT = "https://%s" % SRM_HOST
BASE_FILE_PATH=props['storm.ptg.base_file_path']
NUM_FILES=int(props['storm.ptg.num_files'])
MAX_WAITING_TIME_IN_MSEC=int(props['storm.ptg.max_waiting_time_in_msec'])

SURL_PREFIX="srm://%s/%s" % (SRM_HOST,BASE_FILE_PATH)

## This currently unused method is how you should initialize
## the Grinder SSL module when you want to use a proxy for HTTP requests.
def setup_keymanager():
    cred = PEMCredential(FileInputStream(PROXY_FILE), None)
    key_managers = array((cred.getKeyManager(),), X509ExtendedKeyManager)
    grinder.SSLControl.setKeyManagers(key_managers)

def log_properties():
    log("PtG test configuration")
    for k in sorted(props.keys()):
        log("%s : %s" %(k, props[k])) 
            
class TestRunner:    
    def __call__(self):        
        test = Test(1, "StoRM PTG")
        
        client = SRMClientFactory.newSRMClient(SRM_ENDPOINT,PROXY_FILE)
        surl_range = range(1,random.randrange(NUM_FILES))
        surls = []
        
        for i in surl_range:
            surls.append(SURL_PREFIX+"/f"+str(i))
        
        test.record(client)
        
        log("Requesting %d surls..." % surl_range[-1])
        
        res = client.srmPTG(surls,
                            MAX_WAITING_TIME_IN_MSEC)
        
        log("ptg result: %s: %s" % (res.returnStatus.statusCode, 
                                    res.returnStatus.explanation))
        
        statuses = res.getArrayOfFileStatuses().getStatusArray() 
        
        for s in statuses:
            log("%s -> %s" %(s.getSourceSURL(), 
                             s.getStatus().getStatusCode()))