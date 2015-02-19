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
import string

error = grinder.logger.error
info = grinder.logger.info
debug = grinder.logger.debug

props = grinder.properties

def http_put(url,local_file_path,http_client):
                
        info("HTTP PUT %s " % url)
        resp = http_client.put(url,local_file_path)
        return resp

class TestRunner:

    def __call__(self,url,local_file_path,http_client):

        if http_client is None:
            raise Exception("Please set a non-null HTTP client!")

        test = Test(TestID.HTTP_PUT, "HTTP PUT")
        test.record(http_put)
        try:
            return http_put(url,local_file_path,http_client)
        except Exception:
            error("Error executing HTTP PUT: %s" % traceback.format_exc())
            raise