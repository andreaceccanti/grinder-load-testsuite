from net.grinder.script import Test
from net.grinder.script.Grinder import grinder

import random
import string
import os
import commands

# A shorter alias for the grinder.logger.info() method.
log = grinder.logger.info

# Alias for grinder.properties
props = grinder.properties

GLOBUS_DIR=os.environ['HOME'] + '/.globus'
USERCERT=GLOBUS_DIR + '/usercert.pem'
USERKEY=GLOBUS_DIR + '/userkey.pem'
USERPROXY=os.environ['X509_USER_PROXY']
CACERTS="/etc/grid-security/certificates"

WEBDAV_HOST = props['storm.webdav.host']
WEBDAV_PORT = props['storm.webdav.port']
WEBDAV_ENDPOINT = "https://" + WEBDAV_HOST + ":" + WEBDAV_PORT + "/webdav"

VO = props['test.vo']
REMOTE_INPUT_DIR = props['test.inputdir']
REMOTE_OUTPUT_DIR = props['test.outputdir']

def randomword(length):
	return ''.join(random.choice(string.lowercase) for i in range(length))

class StoRMWebDAV:

	def __init__(self, endpoint):
		self._endpoint = endpoint

	def execute(self, command):
		output=commands.getoutput(command)
		return output

	def getCurlOptions(self):
		return "--cert " + USERPROXY + " --cacert " + USERCERT + " --capath " + CACERTS

	def getDavURL(self, vo, remotepath):
		return self._endpoint + "/" + vo + "/" + remotepath

	def doHead(self, vo, remotepath):
		return self.execute("curl " + self.getCurlOptions() + " --head " + self.getDavURL(vo, remotepath))

	def doMkCol(self, vo, remotepath):
		return self.execute("curl " + self.getCurlOptions() + " -X MKCOL " + self.getDavURL(vo, remotepath))

	def doMove(self, srcvo, srcpath, destvo, destpath):
		return self.execute("curl " + self.getCurlOptions() + " -X MOVE " + self.getDavURL(srcvo, srcpath) + " --header 'Destination:" + self.getDavURL(destvo, destpath) + "'")

class RenamingTest:

	def __init__(self, remotefile, filename):
		self._inputfile = remotefile
		self._vo = VO
		self._l1 = REMOTE_OUTPUT_DIR + "/" + self.randomword(15)
		self._l2 = self._l1 + "/" + self.randomword(15)
		self._outputfile = self._l2 + "/" + filename
		self.webdav = StoRMWebDAV(WEBDAV_ENDPOINT)

	def randomword(self, length):
		return ''.join(random.choice(string.lowercase) for i in range(length))

	def __call__(self):
		self.webdav.doHead(self._vo, self._inputfile)
		self.webdav.doHead(self._vo, self._outputfile)
		self.webdav.doHead(self._vo, self._l2)
		self.webdav.doHead(self._vo, self._l1)
		self.webdav.doMkCol(self._vo, self._l1)
		self.webdav.doMkCol(self._vo, self._l2)
		self.webdav.doMove(self._vo, self._inputfile, self._vo, self._outputfile)

class TestRunner:

	def computeID(self):
		self.agentNum = grinder.getAgentNumber()
		self.threadNum = grinder.getThreadNumber()
		self.procNum = grinder.getProcessNumber()
		self.totThreads = props.getInt("grinder.threads", 1)
		self.totRuns = props.getInt("grinder.runs", 1)
		self.runNum = grinder.getRunNumber()
		return self.agentNum*self.totThreads*self.totRuns + self.threadNum*self.totThreads + self.runNum

	def __call__(self):
		id = self.computeID()
		FILE_NAME = "test_" + str(id)
		REMOTE_FILE = REMOTE_INPUT_DIR + "/" + FILE_NAME
		log("[Agent,Process,Thread/Tot,Run/Tot,Filename] = [" + str(self.agentNum) + "," + str(self.procNum) + "," + str(self.threadNum) + "/" + str(self.totThreads) + ", " + str(self.runNum) + "/" + str(self.totRuns) + "," + FILE_NAME + "]")
		renamingTest = RenamingTest(REMOTE_FILE, FILE_NAME)
		test = Test(1, "WebDAV Renaming test")
		test.record(renamingTest)
		renamingTest();
