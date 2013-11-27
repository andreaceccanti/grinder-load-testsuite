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

error = grinder.logger.error
info = grinder.logger.info
debug = grinder.logger.debug

props = grinder.properties

class TestRunner:
    def _run(self, surls, transport_protocols, client):
        info("Requesting surl(s): %s" % surls)

        res = client.srmPtG(surls,
                            transport_protocols)

        log_surl_call_result("ptg",res)
        info("ptg done.")
        return res

    def __call__(self, surls, transport_protocols, client):
        if client is None:
            raise Exception("Please set a non-null SRM client!")

        test = Test(TestID.PTG, "StoRM PTG")
        test.record(self._run)
        try:
            return self._run(surls, transport_protocols, client)
        except Exception:
            error("Error executing ptg: %s" % traceback.format_exc())
            raise
