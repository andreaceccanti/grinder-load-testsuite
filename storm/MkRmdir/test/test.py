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
SRM_HOST = props['storm.fehost']
BASE_FILE_PATH=props['storm.mkrmdir.base_file_path']

## Computed vars
SRM_ENDPOINT = "https://%s" % SRM_HOST
SURL_PREFIX="srm://%s/%s" % (SRM_HOST,BASE_FILE_PATH)

RECURSION = 0

def randomword(length):
	return ''.join(random.choice(string.lowercase) for i in range(length))

class MkDir:

	def __init__(self, dirname):
		self.dirname = dirname
		self.surl = SURL_PREFIX + "/" + self.dirname
		self.client = SRMClientFactory.newSRMClient(SRM_ENDPOINT,PROXY_FILE)

	def checkSuccess(self, output):
		log("%s %s" % (output.getReturnStatus().getStatusCode(), output.getReturnStatus().getExplanation()))
		if not "SRM_SUCCESS" in output.getReturnStatus().getStatusCode().toString(): 
			self.fail()
	
	def __call__(self):
		log("Creating directory %s..." % self.surl)
		self.checkSuccess(self.client.srmMkdir(self.surl))

class RmDir:

	def __init__(self, dirname, recursion):
		self.dirname = dirname
		self.surl = SURL_PREFIX + "/" + self.dirname
		self.client = SRMClientFactory.newSRMClient(SRM_ENDPOINT,PROXY_FILE)
		self.recursion = recursion

	def checkSuccess(self, output):
		log("%s %s" % (output.getReturnStatus().getStatusCode(), output.getReturnStatus().getExplanation()))
		if not "SRM_SUCCESS" in output.getReturnStatus().getStatusCode().toString(): 
			self.fail()
	
	def __call__(self):
		log("Removing directory %s..." % self.surl)
		self.checkSuccess(self.client.srmRmdir(self.surl, self.recursion))


class TestRunner:

	def __call__(self):

		dirname = randomword(15)
		
		mkdir = MkDir(dirname)
		rmdir = RmDir(dirname,RECURSION)

		tMkdir = Test(100, "StoRM Mkdir")
		tMkdir.record(mkdir)
		
		tRmdir = Test(200, "StoRM Rmdir")
		tRmdir.record(rmdir)
		
		mkdir()
		rmdir()
