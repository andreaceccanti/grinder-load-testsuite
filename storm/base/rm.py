from common import TestID
from exceptions import Exception
from net.grinder.script import Test
from net.grinder.script.Grinder import grinder
import traceback

error = grinder.logger.error
debug = grinder.logger.debug

def rm(surls, client):

	debug("srmRm %s ... " % surls)
	response = client.srmRm(surls)
	debug("srmRm %s response is %s %s" % (surls, response.returnStatus.statusCode, response.returnStatus.explanation))
	return response

class TestRunner:

	def __call__(self, surls, client):

		if client is None:
			raise Exception("Please set a non-null SRM client!")

		test = Test(TestID.RM, "StoRM RM")
		test.record(rm)
		
		try:
			return rm(surls, client)
		except Exception:
			error("Error executing rmdir: %s" % traceback.format_exc())
			raise
