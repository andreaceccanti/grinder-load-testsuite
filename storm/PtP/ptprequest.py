from common import TestID, load_common_properties
from org.italiangrid.srm.client import SRMClient, SRMClientFactory
from eu.emi.security.authn.x509.impl import PEMCredential
from gov.lbl.srm.StorageResourceManager import TStatusCode
import random
import string
import os
import uuid
from net.grinder.script import Test
from net.grinder.script.Grinder import grinder
import mkdir,rmdir

# this loads the base properties inside grinder properties
load_common_properties()

error          = grinder.logger.error
info           = grinder.logger.info
debug          = grinder.logger.debug

props          = grinder.properties

### Custom properties settings  ###
PROXY_FILE = props['storm.ptp.proxy']
SRM_HOST = props['storm.host']
SRM_ENDPOINT = "https://%s" % SRM_HOST
BASE_FILE_PATH=props['storm.ptp.base_file_path']
SURL_PREFIX="srm://%s/%s" % (SRM_HOST,BASE_FILE_PATH)
MAX_WAITING_TIME_IN_MSEC=int(props['storm.ptp.max_waiting_time_in_msec'])

SRM_CLIENT = SRMClientFactory.newSRMClient(SRM_ENDPOINT, PROXY_FILE)

WAITING_STATES = [TStatusCode.SRM_REQUEST_QUEUED, TStatusCode.SRM_REQUEST_INPROGRESS]
SRM_SUCCESS = TStatusCode.SRM_SUCCESS


def status_code(resp):
    return resp.returnStatus.statusCode

def explanation(resp):
    return resp.returnStatus.explanation

def check_success(res, msg):
    if status_code(res) != SRM_SUCCESS:
        error_msg = "%s. %s (expl: %s)" % (msg, status_code(res), explanation(res))
        raise Exception(error_msg)

def getRandomNamr(length):
   return ''.join(random.choice(string.lowercase) for i in range(length))

def setup(client):

	debug("Setting up PTP test.")

	debug("Creating common base dir: " + SURL_PREFIX)

	mkdir_runner = mkdir.TestRunner()
	mkdir_runner(SURL_PREFIX, client)

	debug("Common base directory succesfully created.")

	id = str(uuid.uuid4())
	surl_base_dir = "%s/%s" % (SURL_PREFIX, id)

	debug("Creating thread base dir: " + surl_base_dir)

	mkdir_runner(surl_base_dir, client)

	debug("Thread base directory succesfully created.")

	return surl_base_dir


def  put_request(client, base_dir):
	surls = []

        file_name = "tmp_%s" % (getRandomNamr(12))
	surl = "%s/%s" % (base_dir,file_name)
        surls.append(surl)

	# ptp should be done with a test as well

	res = client.srmPtP(surls,MAX_WAITING_TIME_IN_MSEC)
	while True:
		sres = client.srmSPtP(res)
		if status_code(sres) in WAITING_STATES:
			time.sleep(1)
		else:
			break

	check_success(sres, "Error in PtP for surls (only 5 shown out of %d): %s." % (len(surls), surls[0:5]))
    
	res = client.srmPd(surls, res.requestToken)
	check_success(res, "Error in PD for surls: %s" % surls)


def cleanup(client, base_dir):

	debug("Cleaning up for PtP test.")

	rmdir_runner = rmdir.TestRunner()
	rmdir_runner(base_dir, client, 1)

	debug("Cleanup completed succesfully.")


class TestRunner:

### Executes a ptp and in case of success a pd  ###

    def __call__(self):

	test=Test(TestID.PTP,"StoRM Put without file transfer")

	test.record(put_request)

	base_dir=setup(SRM_CLIENT)
	
	put_request(SRM_CLIENT,base_dir)

	cleanup(SRM_CLIENT,base_dir)

	
