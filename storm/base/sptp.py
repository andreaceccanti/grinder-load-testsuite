from common import TestID
from exceptions import Exception
from net.grinder.script import Test
from net.grinder.script.Grinder import grinder
import traceback

error = grinder.logger.error
debug = grinder.logger.debug

def sptp(ptp_response, client):
    
    token = ptp_response.requestToken
    debug("srmStatusPrepareToPut %s ... " % token )
    response = client.srmSPtP(ptp_response)
    debug("srmStatusPrepareToPut %s response is %s %s" % (token, response.returnStatus.statusCode, response.returnStatus.explanation))
    return response

class TestRunner:

    def __call__(self, ptp_response, client = None):

        if ptp_response is None:
            raise Exception("Please set a non-null PtP response!")

        if client is None:
            raise Exception("Please set a non-null SRM client!")

        test = Test(TestID.SPTP, "StoRM Status PTP")
        test.record(sptp)

        try:
            return sptp(ptp_response, client)
        except Exception, e:
            error("Error executing SPTP: %s" % traceback.format_exc())
            raise
