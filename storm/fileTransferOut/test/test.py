from jarray import array
from net.grinder.plugin.http import HTTPRequest
from net.grinder.script import Test
from net.grinder.script.Grinder import grinder
from org.italiangrid.srm.client import SRMClient, SRMClientFactory
import random
import string
import os

import httplib, urllib

## Alias for grinder.properties
props = grinder.properties

## Alias for grinder info logger
log = grinder.logger.info

## Test parameters fetched from environment vars
PROXY_FILE = os.environ['X509_USER_PROXY']

## Test parameters as fetched from grinder.properties
FE_HOST = props['storm.fehost']
BASE_FILE_PATH=props['storm.ftout.base_file_path']
MAX_WAITING_TIME_IN_MSEC=int(props['storm.ftout.max_waiting_time_in_msec'])
NUM_BYTES = int(props['storm.ftout.num_bytes_transfered'])

# Computed vars
SRM_ENDPOINT = "https://%s" % FE_HOST
SURL_PREFIX="srm://%s/%s" % (FE_HOST,BASE_FILE_PATH)

def randomword(length):
	return ''.join(random.choice(string.lowercase) for i in range(length))

class FileTransferOut:
	def __call__(self):
        
		client = SRMClientFactory.newSRMClient(SRM_ENDPOINT,PROXY_FILE)
		
		surl = SURL_PREFIX+"/"+randomword(15)+".test"
		surls = []
		surls.append(surl)
		
		protocols = []
		protocols.append("http")
		
		# prepare-to-put
		log("srmPrepareToPut %s" % surl)
		res = client.srmPtP(surls,protocols,MAX_WAITING_TIME_IN_MSEC)
		status = res.getArrayOfFileStatuses().getStatusArray(0)
		log("%s %s" % (status.getStatus().getStatusCode(), status.getStatus().getExplanation()))
        
		# file transfer
		turl = res.getArrayOfFileStatuses().getStatusArray(0).getTransferURL()
		log("PUT %s " % turl)
        
		req = HTTPRequest()
		req.setData(randomword(NUM_BYTES))
		resp = req.PUT(turl.toString())
        
		# put done file
		log("srmPutDone %s" % surl)
		res = client.srmPd(surls, res.getRequestToken())
		log("%s %s" % (res.returnStatus.statusCode, res.returnStatus.explanation))


class TestRunner:
	def __call__(self):
        
		req = FileTransferOut()
		
		test = Test(7, "StoRM file-transfer OUT")
		test.record(req)
        
		req()