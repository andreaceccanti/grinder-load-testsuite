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

TESTID = 200

def do_test(pEndpoint, pCaDirname, pClientCert, pClientKey, pClientPasswd, pProxyPath, pResourceId, pActionId):
    lMethodInfo = "do_test"
    log.debug("START %s" % lMethodInfo)
    lPepClient = create_client(pEndpoint, pCaDirname, pClientCert, pClientKey, pClientPasswd)
    lCerts = get_user_cert(pProxyPath)
    lRequest = create_request(lCerts, pResourceId, pActionId)
    lResponse = lPepClient.authorize(lRequest)
    log.debug("END %s" % lMethodInfo)
    return lResponse

def test_permit(self):
    lRange = self.RangePermit.split(",")
    lResourceId = get_resource_id(self, lRange)
    lEndpoint = self.EndpointList[0]
    lMethodInfo = "test_permit - resourceid=[%s]" % lResourceId
    log.debug("START %s" % lMethodInfo)
    lResponse = do_test(lEndpoint, self.CaDirname, self.ClientCert, self.ClientKey, self.ClientPasswd, self.ProxyPath, lResourceId, self.ActionId)
    lResult = lResponse.getResults().get(0)
    lDecision = lResult.getDecision()
    check_result(lDecision, Result.DECISION_PERMIT)
    log.debug("END %s" % lMethodInfo)

def test_deny(self):
    lRange = self.RangeDeny.split(",")
    lResourceId = get_resource_id(self, lRange)
    lEndpoint = self.EndpointList[0]
    lMethodInfo = "test_deny - resourceid=[%s]" % lResourceId
    log.debug("START %s" % lMethodInfo)
    lResponse = do_test(lEndpoint, self.CaDirname, self.ClientCert, self.ClientKey, self.ClientPasswd, self.ProxyPath, lResourceId, self.ActionId)
    lResult = lResponse.getResults().get(0)
    lDecision = lResult.getDecision()
    check_result(lDecision, Result.DECISION_DENY)
    log.debug("END %s" % lMethodInfo)

def test_not_applicable(self):
    lRange = self.RangeNotAppl.split(",")
    lResourceId = get_resource_id(self, lRange)
    lEndpoint = self.EndpointList[0]
    lMethodInfo = "test_not_applicable - resourceid=[%s]" % lResourceId
    log.debug("START %s" % lMethodInfo)
    lResponse = do_test(lEndpoint, self.CaDirname, self.ClientCert, self.ClientKey, self.ClientPasswd, self.ProxyPath, lResourceId, self.ActionId)
    lResult = lResponse.getResults().get(0)
    lDecision = lResult.getDecision()
    check_result(lDecision, Result.DECISION_NOT_APPLICABLE)
    log.debug("END %s" % lMethodInfo)

def authorize_test(self):
    test_permit(self)
    test_deny(self)
    test_not_applicable(self)

class TestRunner:
    def __init__(self):
        lMethodInfo = "init"
        log.debug("START %s" % lMethodInfo)
        load_props(self)
        log.debug("END %s" % lMethodInfo)
        
    def __call__(self):
        lMethodInfo = "call"
        log.debug("START %s" % lMethodInfo)
        
        try:
            lTest = Test(TESTID, "Argus PEPD test")
            lTest.record(authorize_test)
            
            authorize_test(self)
            
        except Exception, e:
            log.error("Error executing PEPD test: %s" % traceback.format_exc())
            
        log.debug("END %s" % lMethodInfo)