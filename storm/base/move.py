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

# this loads the base properties inside grinder properties
load_common_properties()

error = grinder.logger.error
info = grinder.logger.info
debug = grinder.logger.debug

props = grinder.properties

PROXY_FILE = props['client.proxy']
GLOBUS_DIR = os.environ['HOME'] + '/.globus'
USERCERT = GLOBUS_DIR + '/usercert.pem'
USERKEY = GLOBUS_DIR + '/userkey.pem'
CACERTS = "/etc/grid-security/certificates"

WEBDAV_HOST = props['atlas_ren.host']
WEBDAV_PORT = props['atlas_ren.port']
WEBDAV_ENDPOINT = "https://" + WEBDAV_HOST + ":" + WEBDAV_PORT + "/webdav"

def execute(command):
	output = commands.getoutput(command)
	return output

def getCurlOptions():
	return "--cert " + PROXY_FILE + " --cacert " + USERCERT + " --capath " + CACERTS

def getDavURL(vo, remotepath):
	return WEBDAV_ENDPOINT + "/" + vo + "/" + remotepath

def move(src_vo, src_path, dest_vo, dest_path):
	debug("MOVE %s to %s" % (src_path, dest_path))
	return execute("curl " + getCurlOptions() + " -X MOVE " + getDavURL(src_vo, src_path) + " --header 'Destination:" + getDavURL(dest_vo, dest_path) + "'")

class TestRunner:

	def __call__(self, src_vo, src_path, dest_vo, dest_path):

		test = Test(TestID.MOVE, "MOVE")
		test.record(move)

		try:
			return move(src_vo, src_path, dest_vo, dest_path)
		except Exception:
			error("Error executing MOVE: %s" % traceback.format_exc())
			raise