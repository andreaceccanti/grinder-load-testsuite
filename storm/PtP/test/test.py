from org.italiangrid.srm.client import SRMClient, SRMClientFactory
from eu.emi.security.authn.x509.impl import PEMCredential
import random
import string
import os
from net.grinder.script import Test
from net.grinder.script.Grinder import grinder


## Alias for grinder info logger
log = grinder.logger.info

## Alias for grinder.properties
props=grinder.properties

### Custom properties settings  ###
PROXY_FILE = props['storm.ptp.proxy']
SRM_HOST = props['storm.host']
SRM_ENDPOINT = "https://%s" % SRM_HOST
BASE_FILE_PATH=props['storm.ptp.base_file_path']
SURL_PREFIX="srm://%s/%s" % (SRM_HOST,BASE_FILE_PATH)
MAX_WAITING_TIME_IN_MSEC=int(props['storm.ptp.max_waiting_time_in_msec'])

def getRandomNamr(length):
   return ''.join(random.choice(string.lowercase) for i in range(length))

class PutRequest:
	def __call__(self):

		client = SRMClientFactory.newSRMClient(SRM_ENDPOINT,PROXY_FILE)
		surls = []

        	file_name = "tmp_%s" % (getRandomNamr(12))
	        surl = "%s/%s" % (SURL_PREFIX,file_name)
        	surls.append(surl)

	        res = client.srmPtP(surls,MAX_WAITING_TIME_IN_MSEC)
		log("ptp result: %s: %s" % (res.returnStatus.statusCode,res.returnStatus.explanation))

        	statuses = res.getArrayOfFileStatuses().getStatusArray()

	        for s in statuses:
        	    log("%s -> %s" % (s.getSURL(),
                	             s.getStatus().getStatusCode()))

	        requestToken=res.getRequestToken()
        	res = client.srmPd(surls,requestToken)

		log("pd result: %s: %s" % (res.returnStatus.statusCode,res.returnStatus.explanation))

        	statuses = res.getArrayOfFileStatuses().getStatusArray()

	        for s in statuses:
        	    log("%s -> %s" %(s.getSurl(),
                	             s.getStatus().getStatusCode()))


class TestRunner:

### Executes a ptp and in case of success a pd  ###

    def __call__(self):

	test=Test(1,"StoRM Put without file transfer")
	
	request=PutRequest()
	test.record(request)

	request()
