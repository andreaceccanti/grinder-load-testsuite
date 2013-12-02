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


def randomword(length):
    return ''.join(random.choice(string.lowercase) for i in range(length))

def http_put(turls,num_bytes):
                
        info("HTTP PUT %s " % turls)
        
        req = HTTPRequest()
        req.setData(randomword(num_bytes)) 
        resp = req.PUT(turls.toString())               
        
        return resp

class TestRunner:
    def __call__(self,turls,num_bytes):

        test = Test(TestID.HTTP_PUT, "HTTP PUT")
        test.record(http_put)
        try:
            return http_put(turls,num_bytes)
        except Exception:
            error("Error executing HTTP PUT: %s" % traceback.format_exc())
            raise