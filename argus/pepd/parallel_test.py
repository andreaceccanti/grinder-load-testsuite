from net.grinder.script.Grinder import grinder
from net.grinder.script import Test
from org.glite.authz.pep.client import PEPClient, PEPClientException
from org.glite.authz.pep.client.config import PEPClientConfiguration, PEPClientConfigurationException
from org.glite.authz.pep.profile import CommonXACMLAuthorizationProfile
from org.glite.authz.common.security import PEMFileReader
from org.glite.authz.common.model import Request, Response, Result
import os
import traceback
from random import randint
from utils import *

log = grinder.logger
props = grinder.getProperties()

TESTID = 201

def parallel_test(self):
    lRange = self.RangePermit.split(",")
    lResourceId = "%s%03d" % (self.ResourceId, int(lRange[0]))
    lThreadId = grinder.threadNumber
    idx = lThreadId % len(self.EndpointList)
    lEndpoint = self.EndpointList[idx]
    lMethodInfo = "parallel_test - resourceid=[%s] actionid=[%s] endpoint=[%s]" % (lResourceId, self.ActionId, lEndpoint)
    log.debug("START %s" % lMethodInfo)
    lPepClient = create_client(lEndpoint, self.CaDirname, self.ClientCert, self.ClientKey, self.ClientPasswd)
    lCerts = get_user_cert(self.ProxyPath)
    lRequest = create_request(lCerts, lResourceId, self.ActionId)
    self.RequestBarrier.await()
    lResponse = lPepClient.authorize(lRequest)
    lResult = lResponse.getResults().get(0)
    lDecision = lResult.getDecision()
    check_result(lDecision, Result.DECISION_PERMIT)
    log.debug("END %s" % lMethodInfo)

class TestRunner:
    def __init__(self):
        lMethodInfo = "init"
        log.debug("START %s" % lMethodInfo)
        load_props(self)
        self.RequestBarrier = grinder.barrier("Request")
        log.debug("END %s" % lMethodInfo)
        
    def __call__(self):
        lMethodInfo = "call"
        log.debug("START %s" % lMethodInfo)
        
        try:
            lTest = Test(TESTID, "Argus PEPD parallel test")
            lTest.record(parallel_test)
            
            parallel_test(self)
            
        except Exception, e:
            log.error("Error executing PEPD test: %s" % traceback.format_exc())
            
        log.debug("END %s" % lMethodInfo)