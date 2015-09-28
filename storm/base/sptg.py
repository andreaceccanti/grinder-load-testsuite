from common import TestID
from exceptions import Exception
from net.grinder.script import Test
from net.grinder.script.Grinder import grinder
import traceback

error = grinder.logger.error
debug = grinder.logger.debug

def sptg(ptg_response, client):
    
    token = ptg_response.requestToken
    debug("srmStatusPrepareToGet token %s ... " % token )
    response = client.srmSPtG(ptg_response)
    debug("srmStatusPrepareToGet %s response is %s %s" % (token, response.returnStatus.statusCode, response.returnStatus.explanation))
    return response

class TestRunner:
    
    def __call__(self, ptg_response, client=None):
        
        if ptg_response is None:
            raise Exception("Please set a non-null PtG response!")

        if client is None:
            raise Exception("Please set a non-null SRM client!")

        test = Test(TestID.SPTG, "StoRM Status PTG")
        test.record(sptg)

        try:
            return sptg(ptg_response, client)
        except Exception, e:
            error("Error executing sptg: %s" % traceback.format_exc())
            raise
