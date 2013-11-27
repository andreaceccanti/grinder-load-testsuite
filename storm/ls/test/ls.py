from eu.emi.security.authn.x509.impl import PEMCredential
from jarray import array
from java.io import FileInputStream
from javax.net.ssl import X509ExtendedKeyManager
from net.grinder.plugin.http import HTTPRequest
from net.grinder.script import Test
from net.grinder.script.Grinder import grinder
from org.italiangrid.srm.client import SRMClient, SRMClientFactory
import random

# aliases for grinder.properties
props = grinder.properties
log = grinder.logger.info

## test parameters as fetched from grinder.properties
PROXY_FILE = props['storm.ls.proxy']
SRM_HOST = props['storm.host']
MAX_WAITING_TIME_IN_MSEC = int(props['storm.ls.max_waiting_time_in_msec'])

# computed vars
SRM_ENDPOINT = "https://%s" % SRM_HOST

class TestRunner:    

    def __call__(self, surls):

			log("ls")

			test = Test(4, "ls")

			client = SRMClientFactory.newSRMClient(SRM_ENDPOINT, PROXY_FILE)
        
			test.record(client)

			res = client.srmLs(surls, MAX_WAITING_TIME_IN_MSEC)

			log("Result: %s: %s" % (res.returnStatus.statusCode, res.returnStatus.explanation))
			for s in res.getDetails().getPathDetailArray():
				log("%s -> %s" %(s.getPath(), s.getStatus().getStatusCode()))
