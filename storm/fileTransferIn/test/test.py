from eu.emi.security.authn.x509.impl import PEMCredential
from jarray import array
from java.io import FileInputStream
from javax.net.ssl import X509ExtendedKeyManager
from net.grinder.plugin.http import HTTPRequest
from net.grinder.script import Test
from net.grinder.script.Grinder import grinder
from org.italiangrid.srm.client import SRMClient, SRMClientFactory
import random
import os
import java.lang.System, java.util.Random

## Alias for grinder.properties
props = grinder.properties

## Alias for grinder info logger
log = grinder.logger.info

## Test parameters fetched from environment vars
PROXY_FILE = os.environ['X509_USER_PROXY']

## Test parameters as fetched from grinder.properties
FE_HOST = props['storm.fehost']
BASE_FILE_PATH=props['storm.ftin.base_file_path']
NUM_FILES=int(props['storm.ftin.num_files'])
MAX_WAITING_TIME_IN_MSEC=int(props['storm.ftin.max_waiting_time_in_msec'])

# Computed vars
SRM_ENDPOINT = "https://%s" % FE_HOST
SURL_PREFIX="srm://%s/%s" % (FE_HOST,BASE_FILE_PATH)

g_rng = java.util.Random(java.lang.System.currentTimeMillis())

def randNum(i_min, i_max):
	assert i_min <= i_max
	range = i_max - i_min + 1  # re-purposing "range" is legal in Python
	assert range <= 0x7fffffff  # because we're using java.util.Random
	randnum = i_min + g_rng.nextInt(range)
	assert i_min <= randnum <= i_max
	return randnum

class FileTransferIn:
	def __call__(self):
	
		client = SRMClientFactory.newSRMClient(SRM_ENDPOINT,PROXY_FILE)
		
		surl = SURL_PREFIX+"/f"+str(randNum(0,NUM_FILES-1))
		surls = []
		surls.append(surl)
		
		protocols = []
		protocols.append("http")
		
		# prepare-to-get
		log("srmPrepareToGet %s" % surl)
		res = client.srmPTG(surls,protocols,MAX_WAITING_TIME_IN_MSEC)
		status = res.getArrayOfFileStatuses().getStatusArray(0)
		log("%s %s" % (status.getStatus().getStatusCode(), status.getStatus().getExplanation()))

		# file transfer
		turl = res.getArrayOfFileStatuses().getStatusArray(0).getTransferURL()
		log("GET %s " % turl)
		req = HTTPRequest()
		resp = req.GET(turl.toString())

		# release-files
		log("srmReleaseFiles %s" % surl)
		res = client.srmReleaseFiles(res.getRequestToken(), surls)
		log("%s %s" % (res.returnStatus.statusCode, res.returnStatus.explanation))


class TestRunner:
	def __call__(self):

		req = FileTransferIn()
		
		test = Test(6, "StoRM file-transfer IN")
		test.record(req)

		req()