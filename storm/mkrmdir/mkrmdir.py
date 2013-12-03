from common import TestID, load_common_properties
from eu.emi.security.authn.x509.impl import PEMCredential
from exceptions import Exception
from gov.lbl.srm.StorageResourceManager import TStatusCode
from jarray import array
from java.io import FileInputStream
from javax.net.ssl import X509ExtendedKeyManager
from net.grinder.plugin.http import HTTPRequest
from net.grinder.script import Test
from net.grinder.script.Grinder import grinder
from org.italiangrid.srm.client import SRMClient, SRMClientFactory
import mkdir, rmdir
import random
import string
import time
import traceback
import uuid


## This loads the base properties inside grinder properties
## Should be left at the top of the script execution
load_common_properties()

error          = grinder.logger.error
info           = grinder.logger.info
debug          = grinder.logger.debug

props          = grinder.properties

PROXY_FILE     = props['client.proxy']
FE_HOST        = props['storm.host']
BASE_FILE_PATH = props['mkrmdir.base_file_path']

SRM_ENDPOINT   = "https://%s" % FE_HOST
SURL_PREFIX    = "srm://%s/%s" % (FE_HOST, BASE_FILE_PATH)

## Perform an srmPing before running the test to
## rule out the handshake time from the stats
DO_HANDSHAKE = bool(props['mkrmdir.do_handshake'])

def status_code(resp):
    return resp.returnStatus.statusCode

def compute_surl():
	rand_uuid = uuid.uuid4()
	surl = "%s/%s" % (SURL_PREFIX, str(rand_uuid))
	return surl

def mkrmdir(client):

	surl = compute_surl()

	mkdir_runner = mkdir.TestRunner()
	res = mkdir_runner(surl, client)

	if status_code(res) != TStatusCode.SRM_SUCCESS:
		msg = "MkDir failure on surl: %s" % surl
		error(msg)
		raise Exception(msg)

	return surl


def cleanup(client, surl):

	rmdir_runner = rmdir.TestRunner()
	res = rmdir_runner(surl, client)

	if status_code(res) != TStatusCode.SRM_SUCCESS:
		msg = "rmdir failure on surl: %s" % surl
		error(msg)
		raise Exception(msg)

		debug("Cleaned up %s" % surl)


class TestRunner:

	def __call__(self):
		
		try:
			
			test = Test(TestID.MKRMDIR, "Create and then remove a directory")
			test.record(mkrmdir)
			
			client = SRMClientFactory.newSRMClient(SRM_ENDPOINT, PROXY_FILE)

			if DO_HANDSHAKE:
				client.srmPing();

			surl = mkrmdir(client)
			cleanup(client, surl)

		except Exception, e:
			error("Error executing ptp-sync: %s" % traceback.format_exc())
			raise
