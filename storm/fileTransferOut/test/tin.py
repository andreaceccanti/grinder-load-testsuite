from jarray import array
from net.grinder.script import Test
from net.grinder.script.Grinder import grinder
from net.grinder.plugin.http import HTTPRequest
import random
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
NUM_BYTES = int(props['storm.num_bytes_transfered'])

# computed vars
SRM_ENDPOINT = "https://%s" % FE_HOST
SURL_PREFIX="srm://%s/%s" % (FE_HOST, BASE_FILE_PATH)

class TestRunner:
	
	def __call__(self, turl):

		test = Test(102, "Transfer file in using HTTP")

		log("Transfer in")

		req = HTTPRequest(url=turl.toString())

		test.record(req)

		req.setData(''.join(random.choice(string.lowercase) for i in range(NUM_BYTES)))
		req.PUT()
