from common import TestID
from exceptions import Exception
from net.grinder.script import Test
from net.grinder.script.Grinder import grinder
import traceback

error = grinder.logger.error
debug = grinder.logger.debug

def ls(surl, client):
	
	debug("srmLs %s ..." % surl)
	response = client.srmLs([surl], 60000)
	debug("srmLs %s response is %s %s" % (surl, response.returnStatus.statusCode, response.returnStatus.explanation))
	return response

class TestRunner:    

	def __call__(self, surl, client):

		if client is None:
			raise Exception("Please set a non-null SRM client!")

		test = Test(TestID.LS, "StoRM LS")
		test.record(ls)

		try:
			return ls(surl, client)
		except Exception:
			error("Error executing ls: %s" % traceback.format_exc())
			raise
