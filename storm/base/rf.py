from common import TestID
from exceptions import Exception
from net.grinder.script import Test
from net.grinder.script.Grinder import grinder
import traceback

error = grinder.logger.error
debug = grinder.logger.debug

def rf(surl, token, client):

	debug("srmReleaseFile %s with token %s ... " % (surl,token))
	response = client.srmReleaseFiles(token,[surl])
	debug("srmReleaseFile %s response is %s %s" % (surl, response.returnStatus.statusCode, response.returnStatus.explanation))
	return response

class TestRunner:

	def __call__(self, surl, token, client):

		if client is None:
			raise Exception("Please set a non-null SRM client!")

		test = Test(TestID.RF, "StoRM RF")
		test.record(rf)
		
		try:
			return rf(surl, token, client)
		except Exception:
			error("Error executing srmRf: %s" % traceback.format_exc())
			raise
