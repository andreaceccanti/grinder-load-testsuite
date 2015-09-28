from common import *
from exceptions import Exception
from net.grinder.script import Test
from net.grinder.script.Grinder import grinder
import traceback

error = grinder.logger.error
debug = grinder.logger.debug

def rmdir(surl, client, recursive):

	debug("srmRmDir %s ... " % surl)
	response = client.srmRmdir(surl, recursive)
	debug("srmRmDir %s response is %s %s" % (surl, response.returnStatus.statusCode, response.returnStatus.explanation))
	return response

class TestRunner:

	def __call__(self, surl, client, recursive=0):

		if client is None:
			raise Exception("Please set a non-null SRM client!")

		test = Test(TestID.RMDIR, "StoRM RMDIR")
		test.record(rmdir)
		
		try:
			return rmdir(surl, client, recursive)
		except Exception:
			error("Error executing rmdir: %s" % traceback.format_exc())
			raise
