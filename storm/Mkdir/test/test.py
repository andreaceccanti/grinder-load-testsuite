from net.grinder.script import Test
from net.grinder.script.Grinder import grinder
from org.italiangrid.srm.client import SRMClient, SRMClientFactory
import random
import os
import string

## Alias for grinder.properties
props = grinder.properties

## Alias for grinder info logger
log = grinder.logger.info

## Test parameters fetched from environment vars
PROXY_FILE = os.environ['X509_USER_PROXY']

## Test parameters as fetched from grinder.properties
SRM_HOST = props['storm.host']
BASE_FILE_PATH=props['storm.mkdir.base_file_path']

## Computed vars
SRM_ENDPOINT = "https://%s" % SRM_HOST
SURL_PREFIX="srm://%s/%s" % (SRM_HOST,BASE_FILE_PATH)

def randomword(length):
	return ''.join(random.choice(string.lowercase) for i in range(length))

class TestRunner:

	def __call__(self):

		client = SRMClientFactory.newSRMClient(SRM_ENDPOINT,PROXY_FILE)
		surl = SURL_PREFIX + "/" + randomword(15)

		test = Test(1, "StoRM Mkdir")
		test.record(client)

		log("Creating directory %s..." % surl)

		res = client.srmMkdir(surl)

		log("Mkdir result: %s: %s" % (res.returnStatus.statusCode, res.returnStatus.explanation))
