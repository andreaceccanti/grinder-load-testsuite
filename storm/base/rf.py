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

def rf(surl, token, client):

	debug("Releasing file %s with token %s" % (surl,token))

	res= client.srmReleaseFiles(token,[surl])

	debug("File released")
	
	return res


class TestRunner:

	def __call__(self, surl, token, client):

		if client is None:
			raise Exception("Please set a non-null SRM client!")

		test = Test(TestID.RF, "StoRM RF")
		test.record(rf)
		
		try:
			return rf(surl, token, client)
		except Exception:
			error("Error executing srmRf: %s" % traceback.format_exc())
			raise
