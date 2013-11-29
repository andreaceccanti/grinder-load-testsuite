from common import TestID, log_surl_call_result
from eu.emi.security.authn.x509.impl import PEMCredential
from exceptions import Exception
from gov.lbl.srm.StorageResourceManager import TStatusCode
from jarray import array
from java.io import FileInputStream
from javax.net.ssl import X509ExtendedKeyManager
from net.grinder.plugin.http import HTTPRequest
from net.grinder.script import Test
from net.grinder.script.Grinder import grinder
from org.italiangrid.srm.client import SRMClient, SRMClientFactory
import random
import time
import traceback

error = grinder.logger.error
info = grinder.logger.info
debug = grinder.logger.debug

props = grinder.properties

def sptp(ptp_resp, client):
    token = ptp_resp.requestToken
    debug("SPTP for token: %s" % token )

    res = client.srmSPtP(ptp_resp)
    log_surl_call_result("sptp",res)
    return res

class TestRunner:
    def __call__(self, ptp_resp, client = None):
        if ptp_resp is None:
            raise Exception("Please set a non-null PtP response!")

        if client is None:
            raise Exception("Please set a non-null SRM client!")

        test = Test(TestID.SPTP, "StoRM Status PTP")
        test.record(sptp)

        try:
            return sptp(ptp_resp, client)
        except Exception, e:
            error("Error executing SPTP: %s" % traceback.format_exc())
            raise
