from common import TestID
from exceptions import Exception
from net.grinder.script import Test
from net.grinder.script.Grinder import grinder
import traceback

error = grinder.logger.error
debug = grinder.logger.debug

def ptg(surls, transport_protocols, client):

    debug("srmPrepareToGet %s ... " % surls)
    response = client.srmPtG(surls, transport_protocols)
    debug("srmPrepareToGet %s response is %s %s" % (surls, response.returnStatus.statusCode, response.returnStatus.explanation))
    return response

class TestRunner:

    def __call__(self, surls, transport_protocols, client):

        if client is None:
            raise Exception("Please set a non-null SRM client!")

        test = Test(TestID.PTG, "StoRM PTG")
        test.record(ptg)

        try:
            return ptg(surls, transport_protocols, client)
        except Exception:
            error("Error executing ptg: %s" % traceback.format_exc())
            raise
