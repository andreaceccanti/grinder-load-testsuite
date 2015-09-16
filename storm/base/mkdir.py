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

def mkdir(surl, client):
	
    debug("Creating directory: %s" % surl)

    res= client.srmMkdir(surl)

    debug("Directory created")

    return res
	

class TestRunner:

    def __call__(self, surl, client):

        if client is None:
            raise Exception("Please set a non-null SRM client!")

        test = Test(TestID.MKDIR, "StoRM MKDIR")
        test.record(mkdir)

        try:
            return mkdir(surl, client)
        except Exception:
            error("Error executing mkdir: %s" % traceback.format_exc())
            raise
