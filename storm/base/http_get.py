from common import TestID
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


def http_get(url,http_client):
                
        info("HTTP GET %s " % url)
        resp = http_client.get(url)
        return resp

class TestRunner:
    def __call__(self,url,http_client):

        if http_client is None:
            raise Exception("Please set a non-null HTTP client!")

        test = Test(TestID.HTTP_GET, "HTTP GET")
        test.record(http_get)
        try:
            return http_get(url,http_client)
        except Exception:
            error("Error executing HTTP GET: %s" % traceback.format_exc())
            raise