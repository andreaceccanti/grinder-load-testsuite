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

def ptpsync(surls, transport_protocols, max_waiting_time_in_msec, client):
    debug("PTP-SYNC for surl(s): %s" % surls)

    res = client.srmPtP(surls, transport_protocols, max_waiting_time_in_msec)

    log_surl_call_result("ptp-sync", res)
    debug("ptp-sync done.")
    return res

class TestRunner:
    def __call__(self, surls, transport_protocols, max_waiting_time_in_msec, client):
        if client is None:
            raise Exception("Please set a non-null SRM client!")

        test = Test(TestID.PTP_SYNC, "StoRM PTP-SYNC")
        test.record(ptpsync)
        try:
            return ptpsync(surls, transport_protocols, max_waiting_time_in_msec, client)
        except Exception:
            error("Error executing ptp_sync: %s" % traceback.format_exc())
            raise
