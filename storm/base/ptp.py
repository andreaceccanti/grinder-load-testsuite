from common import TestID
from exceptions import Exception
from net.grinder.script import Test
from net.grinder.script.Grinder import grinder
import traceback

error = grinder.logger.error
debug = grinder.logger.debug

def ptp(surls, transport_protocols, client):

    debug("srmPrepareToPut %s ... " % surls)
    response = client.srmPtP(surls, transport_protocols)
    debug("srmPrepareToPut %s response is %s %s" % (surls, response.returnStatus.statusCode, response.returnStatus.explanation))
    return response

class TestRunner:

    def __call__(self, surls, transport_protocols, client):

        if client is None:
            raise Exception("Please set a non-null SRM client!")

        test = Test(TestID.PTP, "StoRM PTP")
        test.record(ptp)

        try:
            return ptp(surls, transport_protocols, client)
        except Exception:
            error("Error executing ptp: %s" % traceback.format_exc())
            raise
