from net.grinder.script import Test
from net.grinder.script.Grinder import grinder
from org.italiangrid.srm.client import SRMClient, SRMClientFactory
import random
import os
import string

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

	def __call__(self, dirname):

		test = Test(105, "mkdir")

		log("mkdir")
		
		surl = SURL_PREFIX + "/" + dirname

		client = SRMClientFactory.newSRMClient(SRM_ENDPOINT, PROXY_FILE)

		test.record(client)

		res= client.srmMkdir(surl)

		log("Result: %s %s" % (res.getReturnStatus().getStatusCode(), res.getReturnStatus().getExplanation()))

		# test fails it is not an SRM_SUCCESS?
