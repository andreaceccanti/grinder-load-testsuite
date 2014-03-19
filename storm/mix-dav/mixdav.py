from common import TestID, load_common_properties, get_proxy_file_path
from eu.emi.security.authn.x509.impl import PEMCredential
from exceptions import Exception
from jarray import array
from net.grinder.script import Test
from net.grinder.script.Grinder import grinder
from org.italiangrid.dav.client import WebDAVClient, WebDAVClientFactory
import mkcol, http_put, http_get, move, delete
import random
import string
import time
import traceback
import uuid
import os


## This loads the base properties inside grinder properties
## Should be left at the top of the script execution
load_common_properties()

error           = grinder.logger.error
info            = grinder.logger.info
debug           = grinder.logger.debug

props           = grinder.properties

# Proxy authorized to write on SRM/WEBDAV endpoints
PROXY_FILE      = get_proxy_file_path()

# Common variables:
TEST_STORAGEAREA = props['common.test_storagearea']

## Endpoints
WEBDAV_ENDPOINT = "https://%s:%s" % (props['common.gridhttps_host'],props['common.gridhttps_ssl_port'])

# Test specific variables
TEST_DIRECTORY  = props['mixdav.test_directory']

HTTP_CLIENT     = WebDAVClientFactory.newWebDAVClient(WEBDAV_ENDPOINT,PROXY_FILE)

def check_http_success(statusCode, expected_code, error_msg):
    if (statusCode != expected_code):
        msg = "%s. Status code is %s instead of %s" % (error_msg, statusCode, expected_code)
        raise Exception(msg)

def create_test_directory_if_needed(DAV_client):
    test_dir_url = "%s/webdav/%s/%s" % (WEBDAV_ENDPOINT, TEST_STORAGEAREA, TEST_DIRECTORY)
    statusCode = DAV_client.get(test_dir_url)
    if (statusCode != 200):
        statusCode = DAV_client.mkcol(test_dir_url)
        check_http_success(statusCode, 201)

def create_local_file_to_upload():
    local_file_path = "/tmp/%s" % str(uuid.uuid4());
    file = open(local_file_path, "w")
    print >> file, "testo di prova"
    file.close()
    return local_file_path

def setup(DAV_client):
    info("Setting up Mix-WebDAV test.")
    create_test_directory_if_needed(DAV_client)
    local_file_path = create_local_file_to_upload()
    info("Mix-WebDAV test setup completed.")
    return local_file_path

def mix_dav(DAV_client, local_file_path):

    target_dir_name   = str(uuid.uuid4());
    target_file_name  = str(uuid.uuid4());
    target_dir_url    = "%s/webdav/%s/%s/%s" % (WEBDAV_ENDPOINT, TEST_STORAGEAREA, TEST_DIRECTORY, target_dir_name)
    target_file_url   = "%s/webdav/%s/%s/%s/%s" % (WEBDAV_ENDPOINT, TEST_STORAGEAREA, TEST_DIRECTORY, target_dir_name, target_file_name)
    target_file_url2   = "%s/webdav/%s/%s/%s/%s2" % (WEBDAV_ENDPOINT, TEST_STORAGEAREA, TEST_DIRECTORY, target_dir_name, target_file_name)

    mkcol_runner = mkcol.TestRunner()
    mkcol_runner(target_dir_url,DAV_client)

    http_put_runner=http_put.TestRunner()
    statusCode = http_put_runner(target_file_url,local_file_path,DAV_client)
    check_http_success(statusCode, 201, "Error in HTTP PUT")
    
    http_get_runner=http_get.TestRunner()
    statusCode = http_get_runner(target_file_url,DAV_client)
    check_http_success(statusCode, 200, "Error in HTTP GET")
    
    http_get_runner=http_get.TestRunner()
    statusCode = http_get_runner(target_dir_url,DAV_client)
    check_http_success(statusCode, 200, "Error in HTTP GET")

    move_runner = move.TestRunner()
    move_runner(target_file_url,target_file_url2,DAV_client)

    delete_runner = delete.TestRunner()
    delete_runner(target_dir_url,DAV_client)


class TestRunner:

	def __call__(self):		
		try:
			test = Test(TestID.MIX_DAV, "StoRM Mix WebDAV test")
			test.record(mix_dav)

			local_file_path = setup(HTTP_CLIENT)
			mix_dav(HTTP_CLIENT, local_file_path)

		except Exception, e:
			error("Error executing file-transfer-in: %s" % traceback.format_exc())
