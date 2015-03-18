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

error            = grinder.logger.error
info             = grinder.logger.info
debug            = grinder.logger.debug

props            = grinder.properties

# Proxy authorized to write on SRM/WEBDAV endpoints
PROXY_FILE       = get_proxy_file_path()

# Test specific variables
TEST_DIRECTORY   = "putdav"
TEST_STORAGEAREA = props['putdav.storagearea']
TEST_ENDPOINT    = props['putdav.endpoint']
TEST_FILESIZE    = int(props['putdav.filesize'])

# Computed variables
TEST_DIRECTORY_URL = "%s/webdav/%s/%s" % (TEST_ENDPOINT, TEST_STORAGEAREA, TEST_DIRECTORY)

# HTTP Client
DAV_CLIENT       = WebDAVClientFactory.newWebDAVClient(TEST_ENDPOINT,PROXY_FILE)

LOCAL_FILE       = "/tmp/%s" % str(uuid.uuid4())

def getURLFile(filename):
    return "%s/%s" % (TEST_DIRECTORY_URL, filename)

def check_http_success(statusCode, expected_codes, error_msg):
    if (int(statusCode) not in expected_codes):
        msg = "%s. Status code is %s instead of %s" % (error_msg, statusCode, expected_codes)
        raise Exception(msg)

def create_test_directory_if_needed():
    http_get_runner=http_get.TestRunner()
    statusCode = http_get_runner(TEST_DIRECTORY_URL,DAV_CLIENT)
    if (statusCode != 200):
        DAV_CLIENT.mkcol(TEST_DIRECTORY_URL)

def create_local_file():
    info("Creating local file %s" % LOCAL_FILE)
    file = open(LOCAL_FILE, "w")
    file.seek(TEST_FILESIZE*1024-1)
    file.write("\0")
    file.close()
    size = os.stat(LOCAL_FILE).st_size
    info("Local file size is %i bytes" % size)
    return

def upload_file(local_file_path, destination_URL):
    http_put_runner=http_put.TestRunner()
    statusCode = http_put_runner(destination_URL,local_file_path,DAV_CLIENT)
    check_http_success(statusCode, [201], "Error in HTTP PUT")
    return

def setup():
    info("Setting up PUT-WebDAV test.")
    create_test_directory_if_needed()
    create_local_file()
    info("PUT-WebDAV test setup completed.")
    return

def remove_file(target_URL):
    delete_runner = delete.TestRunner()
    delete_runner(target_URL,DAV_CLIENT)
    return

def put_dav(fileURL):
    http_put_runner=http_put.TestRunner()
    statusCode = http_put_runner(fileURL, LOCAL_FILE, DAV_CLIENT)
    check_http_success(statusCode, [201,204], "Error in HTTP PUT")

class TestRunner:

    def isInitThread(self):
        return (grinder.threadNumber == 0)

    def isFirstRun(self):
        return (grinder.runNumber == 0)

    def __init__(self):
        self.initBarrier = grinder.barrier("InitializationDone")
        self.delBarrier = grinder.barrier("ExecutionDone")
        if (self.isInitThread()):
            setup()
        # each thread has its own destination URL
        self.remote_URL = getURLFile(str(uuid.uuid4()));

    def __call__(self):
        if (self.isFirstRun()):
            self.initBarrier.await()
        try:
            test = Test(TestID.PUT_DAV, "StoRM PUT WebDAV test")
            test.record(put_dav)
            put_dav(self.remote_URL)
        except Exception, e:
            error("Error executing put-dav: %s" % traceback.format_exc())

    def __del__(self):
        info("File to remove: %s" % self.remote_URL)
        DAV_CLIENT.delete(self.remote_URL)
        self.delBarrier.await()
        if (self.isInitThread()):
            try:
                info("Removing %s ... " % LOCAL_FILE)
                os.remove(LOCAL_FILE)
                info("Removed %s" % LOCAL_FILE)
            except OSError:
                pass