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

log = grinder.logger
props = grinder.getProperties()

def not_null(pLabel, pValue):
    test = (pValue is None) or (pValue is not None and pValue == "")
    if test:
        raise Exception("%s is empty" % pLabel)

def check_result(pValue, pExpected):
    if pValue != pExpected:
        msg = "Result value mismatch. Obtained [%s] instead of [%s]" % (pValue, pExpected)
        raise Exception(msg)
    
def get_resource_id(self, lRange):
    lRand = randint(int(lRange[0]), int(lRange[1]))
    lResourceId = "%s%03d" % (self.ResourceId, lRand)
    return lResourceId

def create_client(pEndpoint, pCaDirname, pClientCert, pClientKey, pClientPasswd):
    lMethodInfo = "create_client - endpoint=[%s] cert=[%s] key=[%s]" % (pEndpoint, pClientCert, pClientKey)
    log.debug("START %s" % lMethodInfo)
    lConfig = PEPClientConfiguration()
    lConfig.addPEPDaemonEndpoint(pEndpoint)
    lConfig.setTrustMaterial(pCaDirname)
    lConfig.setKeyMaterial(pClientCert, pClientKey, pClientPasswd)
    lPepClient= PEPClient(lConfig)
    log.debug("END %s" % lMethodInfo)
    return lPepClient

def get_user_cert(pProxyPath):
    lMethodInfo = "ger_user_cert - proxypath=[%s]" % pProxyPath
    log.debug("START %s" % lMethodInfo)
    lReader = PEMFileReader()
    lCerts = lReader.readCertificates(pProxyPath)
    log.debug("END %s" % lMethodInfo)
    return lCerts

def create_request(pUserCerts, pResourceId, pActionId):
    lMethodInfo = "create_request - resourceid=[%s] actionid=[%s]" % (pResourceId, pActionId)
    log.debug("START %s" % lMethodInfo)
    lProfile = CommonXACMLAuthorizationProfile.getInstance()
    lRequest = lProfile.createRequest(pUserCerts, pResourceId, pActionId)
    log.debug("END %s" % lMethodInfo)
    return lRequest

def load_props(self):
    lMethodInfo = "load_props"
    log.debug("START %s" % lMethodInfo)
    self.CaDirname = props["common.cadirname"]
    self.ClientCert = props["common.clientcert"]
    self.ClientKey = props["common.clientkey"]
    self.ClientPasswd = props["common.clientpasswd"]
    self.Endpoints = props["common.pepd.endpoints"]
    self.EndpointList = self.Endpoints.split()
    self.ResourceId = props["common.pepd.resourceid"]
    self.RangePermit = props["common.pepd.resourceid.range.permit"]
    self.RangeDeny = props["common.pepd.resourceid.range.deny"]
    self.RangeNotAppl = props["common.pepd.resourceid.range.notappl"]
    self.ActionId = props["common.pepd.actionid"]
    uid = os.geteuid()
    self.ProxyPath = os.getenv('X509_USER_PROXY', "/tmp/x509up_u%s" % uid)
    log.debug("END %s" % lMethodInfo)
