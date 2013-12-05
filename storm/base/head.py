from common import TestID, log_surl_call_result, load_common_properties
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

def head(url, client):
	debug("HEAD %s " % url)
	client.head(url)

class TestRunner:

	def __call__(self, url, client):

		if client is None:
			raise Exception("Please set a non-null WebDAV client!")

		test = Test(TestID.HEAD, "HEAD")
		test.record(head)

		try:
			return head(url, client)
		except Exception:
			error("Error executing HEAD: %s" % traceback.format_exc())
			raise