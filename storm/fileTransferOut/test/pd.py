from jarray import array
from net.grinder.script import Test
from net.grinder.script.Grinder import grinder
from org.italiangrid.srm.client import SRMClient, SRMClientFactory
import string
import os
import httplib, urllib

# aliases for grinder stuff
props = grinder.properties
log = grinder.logger.info

# test parameters as fetched from grinder.properties
PROXY_FILE = props['client.proxy']
FE_HOST = props['storm.host']
BASE_FILE_PATH=props['storm.base_file_path']

# computed vars
SRM_ENDPOINT = "https://%s" % FE_HOST
SURL_PREFIX="srm://%s/%s" % (FE_HOST, BASE_FILE_PATH)

class TestRunner:
	
	def __call__(self, surls, token):

		test = Test(103, "pd")

		log("Put done")

		client = SRMClientFactory.newSRMClient(SRM_ENDPOINT, PROXY_FILE)

		test.record(client)

		res = client.srmPd(surls, token)
		
		log("Result: %s %s" % (res.returnStatus.statusCode, res.returnStatus.explanation))
		for status in res.getArrayOfFileStatuses().getStatusArray():
			log("%s -> %s" %(status.getSurl(), status.getStatus().getStatusCode()))