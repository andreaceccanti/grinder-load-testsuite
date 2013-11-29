from common import TestID, log_surl_call_result
from eu.emi.security.authn.x509.impl import PEMCredential
from exceptions import Exception
from jarray import array
from java.io import FileInputStream
from javax.net.ssl import X509ExtendedKeyManager
from net.grinder.plugin.http import HTTPRequest
from net.grinder.script import Test
from net.grinder.script.Grinder import grinder
from org.italiangrid.srm.client import SRMClient, SRMClientFactory
import random
import traceback

error = grinder.logger.error
info = grinder.logger.info
debug = grinder.logger.debug

props = grinder.properties

def pd(surls, token, client):
    debug("Requesting surl(s): %s" % surls)

    res = client.srmPd(surls,
                       token)

    log_surl_call_result("pd", res)
    debug("pd done.")
    return res

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
