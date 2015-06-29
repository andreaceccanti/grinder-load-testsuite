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

def move(src_url, dest_url, client):
	debug("MOVE %s to %s" % (src_url, dest_url))
	client.move(src_url, dest_url)

class TestRunner:

	def __call__(self, src_url, dest_url, client):

		test = Test(TestID.MOVE, "MOVE")
		test.record(move)

		try:
			return move(src_url, dest_url, client)
		except Exception:
			error("Error executing MOVE: %s" % traceback.format_exc())
			raise