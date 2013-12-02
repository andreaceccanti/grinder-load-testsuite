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


def http_get(turls):
                
        info("HTTP GET %s " % turls)
        req = HTTPRequest()
        resp = req.GET(turls.toString())
        return resp

class TestRunner:
    def __call__(self,turls):

        test = Test(TestID.HTTP_GET, "HTTP GET")
        test.record(http_get)
        try:
            return http_get(turls)
        except Exception:
            error("Error executing HTTP GET: %s" % traceback.format_exc())
            raise