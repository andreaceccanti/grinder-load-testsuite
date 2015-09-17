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

def rmdir(dirname, client, recursive):

	debug("Removing directory: %s" % dirname)

	res= client.srmRmdir(dirname, recursive)

	debug("Directory removed")
	
	return res


class TestRunner:

	def __call__(self, dirname, client, recursive=0):

		if client is None:
			raise Exception("Please set a non-null SRM client!")

		test = Test(TestID.RMDIR, "StoRM RMDIR")
		test.record(rmdir)
		
		try:
			return rmdir(dirname, client, recursive)
		except Exception:
			error("Error executing rmdir: %s" % traceback.format_exc())
			raise
