from eu.emi.security.authn.x509.impl import PEMCredential
from jarray import array
from java.io import FileInputStream
from javax.net.ssl import X509ExtendedKeyManager
from net.grinder.plugin.http import HTTPRequest
from net.grinder.script import Test
from net.grinder.script.Grinder import grinder
import random
import ls

# aliases for grinder props
props = grinder.properties
log = grinder.logger.info

## test parameters as fetched from grinder.properties
SRM_HOST = props['storm.host']
BASE_FILE_PATH = props['storm.ls.base_file_path']
NUM_FILES = int(props['storm.ls.num_files'])
NUM_SURLS = int(props['storm.ls.num_surls'])
MAX_WAITING_TIME_IN_MSEC = int(props['storm.ls.max_waiting_time_in_msec'])

# computed vars
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

	def __call__(self):        
        
		surls = []
		for i in range(0, NUM_SURLS):
			surls.append(SURL_PREFIX + "/f" + str(random.randrange(1, NUM_FILES + 1)))
        
			lsTestRunner = ls.TestRunner()
			lsTestRunner(surls)
