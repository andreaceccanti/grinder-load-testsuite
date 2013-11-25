from net.grinder.script import Test
from net.grinder.script.Grinder import grinder
from org.italiangrid.srm.client import SRMClient, SRMClientFactory
import os

## Alias for grinder.properties
props = grinder.properties

## Alias for grinder info logger
log = grinder.logger.info

## Test parameters fetched from environment vars
PROXY_FILE = os.environ['X509_USER_PROXY']

## Test parameters as fetched from grinder.properties
FE_HOST = props['storm.fehost']
BASE_FILE_PATH=props['storm.rmdir.base_file_path']
NUM_DIRECTORIES=int(props['storm.rmdir.num_files'])

# Computed vars
SRM_ENDPOINT = "https://%s" % FE_HOST
SURL_PREFIX="srm://%s/%s" % (FE_HOST,BASE_FILE_PATH)
RECURSION = 0

class Rmdir:

	def fail(self):
		grinder.statistics.getForLastTest().setSuccess(False)

	def print_details(self):
		msg = "[Agent,Process/TotProcesses,Thread/TotThreads,Run/TotRuns,ID] = "
		msg = msg + "[" + str(self.agentNum) + ","
		msg = msg + str(self.procNum) + "/" + str(self.totProcs) + ","
		msg = msg + str(self.threadNum) + "/" + str(self.totThreads) + ","
		msg = msg + str(self.runNum) + "/" + str(self.totRuns) + ","
		msg = msg + str(self.id) + "]"
		log(msg)

	def init(self):
		self.agentNum = grinder.getAgentNumber()
		self.threadNum = grinder.getThreadNumber()
		self.procNum = grinder.getProcessNumber()
		self.totThreads = props.getInt("grinder.threads", 1)
		self.totRuns = props.getInt("grinder.runs", 1)
		self.totProcs = props.getInt("grinder.processes", 1)
		self.runNum = grinder.getRunNumber()
		self.id = self.runNum + self.totRuns*(self.threadNum + self.totThreads*(self.procNum + self.totProcs*(self.agentNum)))
		self.surl = SURL_PREFIX+"/dir_"+str(self.id)
		self.client = SRMClientFactory.newSRMClient(SRM_ENDPOINT,PROXY_FILE)
		self.recursion = RECURSION

	def __call__(self):
	
		self.init() # compute id
		self.print_details()
		
		log("srmRmdir %s" % self.surl)
		res = self.client.srmRmdir(self.surl, self.recursion)
		log("%s %s" % (res.getReturnStatus().getStatusCode(), res.getReturnStatus().getExplanation()))
		
		if not "SRM_SUCCESS" in res.getReturnStatus().getStatusCode().toString(): 
			self.fail()

class TestRunner:
	def __call__(self):

		req = Rmdir()
		
		test = Test(9, "StoRM Rmdir")
		test.record(req)

		req()