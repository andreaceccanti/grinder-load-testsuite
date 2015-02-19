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
TEST_DIRECTORY   = "getdav"
TEST_STORAGEAREA = props['getdav.storagearea']
TEST_ENDPOINT    = props['getdav.endpoint']
TEST_NUMFILES    = int(props['getdav.numfiles'])
TEST_FILESIZE    = int(props['getdav.filesize'])

# Computed variables
TEST_DIRECTORY_URL = "%s/webdav/%s/%s" % (TEST_ENDPOINT, TEST_STORAGEAREA, TEST_DIRECTORY)

# HTTP Client
DAV_CLIENT       = WebDAVClientFactory.newWebDAVClient(TEST_ENDPOINT,PROXY_FILE)

FILE_URLS = []

def getURLFile(filename):
    return "%s/%s" % (TEST_DIRECTORY_URL, filename)

def check_http_success(statusCode, expected_code, error_msg):
    if (statusCode != expected_code):
        msg = "%s. Status code is %s instead of %s" % (error_msg, statusCode, expected_code)
        raise Exception(msg)

def create_test_directory_if_needed():
    http_get_runner=http_get.TestRunner()
    statusCode = http_get_runner(TEST_DIRECTORY_URL,DAV_CLIENT)
    if (statusCode != 200):
        DAV_CLIENT.mkcol(TEST_DIRECTORY_URL)

def create_local_file_to_upload():
    local_file_path = "/tmp/%s" % str(uuid.uuid4());
    info("Creating local file %s" % local_file_path)
    file = open(local_file_path, "w")
    file.seek(TEST_FILESIZE*1024-1)
    file.write("\0")
    file.close()
    size = os.stat(local_file_path).st_size
    info("Local file size is %i bytes" % size)
    return local_file_path

def upload_file(local_file_path, destination_URL):
    http_put_runner=http_put.TestRunner()
    statusCode = http_put_runner(destination_URL,local_file_path,DAV_CLIENT)
    check_http_success(statusCode, 201, "Error in HTTP PUT")
    return

def setup():
    info("Setting up GET-WebDAV test.")
    local_file_path = create_local_file_to_upload()
    for i in range(0,TEST_NUMFILES):
        fileURL = getURLFile(str(uuid.uuid4()));
        upload_file(local_file_path, fileURL)
        FILE_URLS.append(fileURL)
    info("FILE_URLS contains %i elements" % len(FILE_URLS))
    info("GET-WebDAV test setup completed.")
    return

def get_dav(fileURL):
    http_get_runner=http_get.TestRunner()
    statusCode = http_get_runner(fileURL,DAV_CLIENT)
    check_http_success(statusCode, 200, "Error in HTTP GET")

class TestRunner:

    def __init__(self):
        self.initBarrier = grinder.barrier("InitializationDone")
        self.delBarrier = grinder.barrier("ExecutionDone")
        if (grinder.threadNumber == 0):
            create_test_directory_if_needed()
            FILE_URLS = setup()

    def __call__(self):
        if (grinder.runNumber == 0):
            self.initBarrier.await()
        try:
            test = Test(TestID.GET_DAV, "StoRM GET WebDAV test")
            test.record(get_dav)
            get_dav(random.choice(FILE_URLS))
        except Exception, e:
            error("Error executing get-dav: %s" % traceback.format_exc())

    def __del__(self):
        self.delBarrier.await()
        if (grinder.threadNumber == 0):
            info("Thread num. %i is the deleter" % grinder.threadNumber)
            for i in range(0,TEST_NUMFILES):
                info("file to remove: %s" % FILE_URLS[i])
                DAV_CLIENT.delete(FILE_URLS[i])