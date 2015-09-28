from common import TestID
from exceptions import Exception
from net.grinder.script import Test
from net.grinder.script.Grinder import grinder
import traceback

error = grinder.logger.error
debug = grinder.logger.debug

def pd(surls, token, client):

    debug("srmPutDone %s ... " % surls)
    response = client.srmPd(surls, token)
    debug("srmPutDone %s response is %s %s" % (surls, response.returnStatus.statusCode, response.returnStatus.explanation))
    return response

class TestRunner:

    def __call__(self, surls, token, client):
        
        if client is None:
            raise Exception("Please set a non-null SRM client!")

        test = Test(TestID.PD, "StoRM PD")
        test.record(pd)

        try:
            return pd(surls, token, client)
        except Exception:
            error("Error executing pd: %s" % traceback.format_exc())
            raise
