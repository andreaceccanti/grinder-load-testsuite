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

def ptp(surls, transport_protocols, client):
    debug("PTP for surl(s): %s" % surls)

    res = client.srmPtP(surls,
                        transport_protocols)

    log_surl_call_result("ptp", res)
    debug("ptp done.")
    return res

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
