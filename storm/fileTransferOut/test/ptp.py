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
MAX_WAITING_TIME_IN_MSEC=int(props['storm.max_waiting_time_in_msec'])

# computed vars
SRM_ENDPOINT = "https://%s" % FE_HOST
SURL_PREFIX="srm://%s/%s" % (FE_HOST, BASE_FILE_PATH)

class TestRunner:
	
	def __call__(self, surls):

		test = Test(101, "ptp")

		log("Prepare to put")

		client = SRMClientFactory.newSRMClient(SRM_ENDPOINT, PROXY_FILE)

		protocols = []
		protocols.append("http")

		test.record(client)

		res = client.srmPtP(surls, protocols, MAX_WAITING_TIME_IN_MSEC)

		log("Prepare to put result: %s: %s" % (res.returnStatus.statusCode,res.returnStatus.explanation))
		for status in res.getArrayOfFileStatuses().getStatusArray():
			log("%s -> %s" %(status.getSURL(), status.getStatus().getStatusCode()))

		return res