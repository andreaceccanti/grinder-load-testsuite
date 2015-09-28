from common import Utils, TestID
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

utils           = Utils(grinder.properties)

# Get common variables:
TEST_STORAGEAREA = props['common.test_storagearea']

# Test specific variables
TEST_DIRECTORY  = props['mixdav.test_directory']


def get_url(protocol, endpoint, storagearea, path):
    
    return "%s://%s/webdav/%s/%s" % (protocol, endpoint, storagearea, path)

def check_http_success(statusCode, expected_code, error_msg):
    
    if (statusCode != expected_code):
        msg = "%s. Status code is %s instead of %s" % (error_msg, statusCode, expected_code)
        raise Exception(msg)

def create_test_directory_if_needed():
    
    endpoint,client = utils.get_dav_client()
    test_dir_url = get_url("https", endpoint, TEST_STORAGEAREA, TEST_DIRECTORY)
    http_get_runner=http_get.TestRunner()
    statusCode = http_get_runner(test_dir_url, client)
    if (statusCode != 200):
        client.mkcol(test_dir_url)

def create_local_file_to_upload():
    
    local_file_path = "/tmp/%s" % str(uuid.uuid4());
    file = open(local_file_path, "w")
    print >> file, "testo di prova"
    file.close()
    return local_file_path

def setup():
    
    info("Setting up Mix-WebDAV test.")
    local_file_path = create_local_file_to_upload()
    info("Mix-WebDAV test setup completed.")
    return local_file_path

def mix_dav(local_file_path):

    endpoint,client = utils.get_dav_client()
    protocol = "https"
        
    dir_path = "%s/%s" % (TEST_DIRECTORY, str(uuid.uuid4()))
    file1_path = "%s/%s" % (dir_path, str(uuid.uuid4()))                      
    file2_path = "%s_2" % file1_path
         
    target_dir_url = get_url(protocol, endpoint, TEST_STORAGEAREA, dir_path)
    target_file_url = get_url(protocol, endpoint, TEST_STORAGEAREA, file1_path)
    target_file_url2 = get_url(protocol, endpoint, TEST_STORAGEAREA, file2_path)
    
    mkcol_runner = mkcol.TestRunner()
    mkcol_runner(target_dir_url,client)

    http_put_runner=http_put.TestRunner()
    statusCode = http_put_runner(target_file_url,local_file_path,client)
    check_http_success(statusCode, 201, "Error in HTTP PUT")

    http_put_runner=http_put.TestRunner()
    statusCode = http_put_runner(target_file_url,local_file_path,client)
    check_http_success(statusCode, 204, "Error in HTTP PUT")

    http_get_runner=http_get.TestRunner()
    statusCode = http_get_runner(target_file_url,client)
    check_http_success(statusCode, 200, "Error in HTTP GET")
    
    http_get_runner=http_get.TestRunner()
    statusCode = http_get_runner(target_dir_url,client)
    check_http_success(statusCode, 200, "Error in HTTP GET")

    move_runner = move.TestRunner()
    move_runner(target_file_url,target_file_url2,client)

    delete_runner = delete.TestRunner()
    delete_runner(target_dir_url,client)


class TestRunner:

    def __init__(self):
        create_test_directory_if_needed()
        self.local_file_path = setup()

    def __call__(self):
        try:
            test = Test(TestID.MIX_DAV, "StoRM Mix WebDAV test")
            test.record(mix_dav)
            mix_dav(self.local_file_path)

        except Exception, e:
            error("Error executing mix-dav: %s" % traceback.format_exc())
