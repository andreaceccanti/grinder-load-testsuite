from common import TestID, load_common_properties
from eu.emi.security.authn.x509.impl import PEMCredential
from net.grinder.script import Test
from net.grinder.script.Grinder import grinder
from org.italiangrid.srm.client import SRMClient, SRMClientFactory
from org.italiangrid.dav.client import WebDAVClient, WebDAVClientFactory
from gov.lbl.srm.StorageResourceManager import TStatusCode
import random
import string
import os
import commands
import traceback
import uuid
import time
import mkdir, http_put, head, move, mkcol, rmdir

# this loads the base properties inside grinder properties
load_common_properties()

error          = grinder.logger.error
info           = grinder.logger.info
debug          = grinder.logger.debug

props          = grinder.properties

PROXY_FILE     = props['client.proxy']
BASE_FILE_PATH = props['atlas_ren.base_file_path']

FE_HOST = props['storm.host']
SRM_ENDPOINT = "https://%s" % FE_HOST
SURL_PREFIX = "srm://%s/%s" % (FE_HOST, BASE_FILE_PATH)

WAITING_STATES = [TStatusCode.SRM_REQUEST_QUEUED, TStatusCode.SRM_REQUEST_INPROGRESS]
SRM_SUCCESS = TStatusCode.SRM_SUCCESS

NUM_FILES = int(props['atlas_ren.num_files'])
NUM_BYTES = int(props['atlas_ren.num_bytes_transferred'])

WEBDAV_HOST = props['atlas_ren.host']
WEBDAV_PORT = props['atlas_ren.port']
WEBDAV_ENDPOINT = "https://" + WEBDAV_HOST + ":" + WEBDAV_PORT + "/webdav"

HTTP_CLIENT =  WebDAVClientFactory.newWebDAVClient(WEBDAV_ENDPOINT, PROXY_FILE)
SRM_CLIENT = SRMClientFactory.newSRMClient(SRM_ENDPOINT, PROXY_FILE)


def randomword(length):
	return ''.join(random.choice(string.lowercase) for i in range(length))

def status_code(resp):
    return resp.returnStatus.statusCode

def explanation(resp):
    return resp.returnStatus.explanation

def check_success(res, msg):
    if status_code(res) != SRM_SUCCESS:
        error_msg = "%s. %s (expl: %s)" % (msg, status_code(res), explanation(res))
        raise Exception(error_msg)

def compute_filename():
    random_index = random.randint(0, NUM_FILES-1)
    filename = "f%d" % (random_index)
    return filename


def setup(client):
    
	debug("Setting up atlas renaming test.")

	debug("Creating common base dir: " + SURL_PREFIX)

	mkdir_runner = mkdir.TestRunner()
	mkdir_runner(SURL_PREFIX, client)
 
	id = str(uuid.uuid4())
	surl_base_dir = "%s/%s" % (SURL_PREFIX, id)
	
	debug("Creating base dir: " + surl_base_dir)
	
	mkdir_runner(surl_base_dir, client)
	
	debug("Base directory succesfully created.")
        
	fname = compute_filename()
	filename = "%s/%s" % (surl_base_dir, fname)
    
	surls = []
	surls.append(filename)
    
	protocols = []
	protocols.append("http")

	# ptp should be done with a test as well

	res = client.srmPtP(surls, protocols)
	while True:
		sres = client.srmSPtP(res)
		if status_code(sres) in WAITING_STATES:
			time.sleep(1)
		else:
			break

	check_success(sres, "Error in PtP for surls (only 5 shown out of %d): %s." % (len(surls), surls[0:5]))
    
	turls = sres.getArrayOfFileStatuses().getStatusArray(0).getTransferURL()
        
	http_put_runner = http_put.TestRunner()
	put_res = http_put_runner(turls, NUM_BYTES)
    
	res = client.srmPd(surls, res.requestToken)
	check_success(res, "Error in PD for surls: %s" % surls)
  
	debug("Atlas renaming setup completed succesfully.")
    
	base_dir = "%s/%s" % (SURL_PREFIX, id)
	webdav_basedir = "%s/%s/%s" % (WEBDAV_ENDPOINT, BASE_FILE_PATH, id)
	dir_level1 = "%s/%s" % (webdav_basedir, randomword(10))
	dir_level2 = "%s/%s" % (dir_level1, randomword(10))    
	src_file = "%s/%s" % (webdav_basedir, fname)
	dest_file = "%s/%s" % (dir_level2, compute_filename())

	return base_dir, src_file, dest_file, dir_level1, dir_level2

def cleanup(client, base_dir):
	debug("Cleaning up for Atlas renaming.")

	rmdir_runner = rmdir.TestRunner()
	rmdir_runner(base_dir, client, 1)

	debug("Atlas renaming cleanup completed succesfully.")

def atlas_renaming(src_file, dest_file, dir_l1, dir_l2, client):
	debug("Renaming file "+ src_file + " to " + dest_file)

	head_runner = head.TestRunner()
	head_runner(src_file, client)
	head_runner(dest_file, client)
	head_runner(dir_l2, client)
	head_runner(dir_l1, client)

	mkcol_runner = mkcol.TestRunner()
	mkcol_runner(dir_l1, client)
	mkcol_runner(dir_l2, client)

	move_runner = move.TestRunner()
	move_runner(src_file, dest_file, client)

	debug("Fineshed renaming file"+ src_file + " to " + dest_file)

class TestRunner:
	
	def __call__(self):		
		
		test = Test(TestID.ATLAS_RENAMING, "Atlas renaming")
		test.record(atlas_renaming)
		
		(base_dir, src_file, dest_file, dir_level1, dir_level2) = setup(SRM_CLIENT)
		
		atlas_renaming(src_file, dest_file, dir_level1, dir_level2, HTTP_CLIENT)
		
		cleanup(SRM_CLIENT, base_dir)
