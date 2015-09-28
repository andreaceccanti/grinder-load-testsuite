from common import TestID
from exceptions import Exception
from net.grinder.script import Test
from net.grinder.script.Grinder import grinder
import traceback

error = grinder.logger.error
debug = grinder.logger.debug

def mkdir(surl, client):
	
    debug("srmMkDir %s ..." % surl)
    response = client.srmMkdir(surl)
    debug("srmMkDir %s response is %s %s" % (surl, response.returnStatus.statusCode, response.returnStatus.explanation))
    return response

class TestRunner:

    def __call__(self, surl, client):

        if client is None:
            raise Exception("Please set a non-null SRM client!")

        test = Test(TestID.MKDIR, "StoRM MKDIR")
        test.record(mkdir)

        try:
            return mkdir(surl, client)
        except Exception:
            error("Error executing mkdir: %s" % traceback.format_exc())
            raise
