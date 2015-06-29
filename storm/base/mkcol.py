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
import os
import commands

error = grinder.logger.error
info = grinder.logger.info
debug = grinder.logger.debug

def mkcol(url, client):
	debug("MKCOL %s" % url)
	client.mkcol(url)

class TestRunner:

	def __call__(self, url, client):

		test = Test(TestID.MKCOL, "MKCOL")
		test.record(mkcol)

		try:
			return mkcol(url, client)
		except Exception:
			error("Error executing MKCOL: %s" % traceback.format_exc())
			raise
