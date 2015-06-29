from common import TestID, Configuration, Utils
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


error           = grinder.logger.error
info            = grinder.logger.info
debug           = grinder.logger.debug

props           = grinder.properties

CONF            = Configuration()
UTILS           = Utils()

## This loads the base properties inside grinder properties
## Should be left at the top of the script execution
CONF.load_common_properties()

# Get common variables:
TEST_STORAGEAREA = CONF.get_test_storagearea()

# Test specific variables
DAV_ENDPOINT,DAV_CLIENT = UTILS.get_DAV_client(CONF)

TEST_DIRECTORY  = props['mixdav.test_directory']

def check_http_success(statusCode, expected_code, error_msg):
    if (statusCode != expected_code):
        msg = "%s. Status code is %s instead of %s" % (error_msg, statusCode, expected_code)
        raise Exception(msg)

def create_test_directory_if_needed(DAV_client):
    test_dir_url = "https://%s/webdav/%s/%s" % (DAV_ENDPOINT, TEST_STORAGEAREA, TEST_DIRECTORY)
    http_get_runner=http_get.TestRunner()
    statusCode = http_get_runner(test_dir_url,DAV_client)
    if (statusCode != 200):
        DAV_client.mkcol(test_dir_url)

def create_local_file_to_upload():
    local_file_path = "/tmp/%s" % str(uuid.uuid4());
    file = open(local_file_path, "w")
    print >> file, "testo di prova"
    file.close()
    return local_file_path

def setup(DAV_client):
    info("Setting up Mix-WebDAV test.")
    local_file_path = create_local_file_to_upload()
    info("Mix-WebDAV test setup completed.")
    return local_file_path

def mix_dav(DAV_client, local_file_path):

    target_dir_name   = str(uuid.uuid4());
    target_file_name  = str(uuid.uuid4());
    target_dir_url    = "https://%s/webdav/%s/%s/%s" % (DAV_ENDPOINT, TEST_STORAGEAREA, TEST_DIRECTORY, target_dir_name)
    target_file_url   = "https://%s/webdav/%s/%s/%s/%s" % (DAV_ENDPOINT, TEST_STORAGEAREA, TEST_DIRECTORY, target_dir_name, target_file_name)
    target_file_url2   = "https://%s/webdav/%s/%s/%s/%s2" % (DAV_ENDPOINT, TEST_STORAGEAREA, TEST_DIRECTORY, target_dir_name, target_file_name)

    mkcol_runner = mkcol.TestRunner()
    mkcol_runner(target_dir_url,DAV_client)

    http_put_runner=http_put.TestRunner()
    statusCode = http_put_runner(target_file_url,local_file_path,DAV_client)
    check_http_success(statusCode, 201, "Error in HTTP PUT")

    http_put_runner=http_put.TestRunner()
    statusCode = http_put_runner(target_file_url,local_file_path,DAV_client)
    check_http_success(statusCode, 204, "Error in HTTP PUT")

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

    def __init__(self):
        self.HTTP_Client = DAV_CLIENT
        create_test_directory_if_needed(self.HTTP_Client)
        self.local_file_path = setup(self.HTTP_Client)

    def __call__(self):
        try:
            test = Test(TestID.MIX_DAV, "StoRM Mix WebDAV test")
            test.record(mix_dav)
            mix_dav(self.HTTP_Client, self.local_file_path)

        except Exception, e:
            error("Error executing mix-dav: %s" % traceback.format_exc())
