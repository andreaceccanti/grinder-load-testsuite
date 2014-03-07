from common import TestID, load_common_properties, get_proxy_file_path
from eu.emi.security.authn.x509.impl import PEMCredential
from exceptions import Exception
from gov.lbl.srm.StorageResourceManager import TStatusCode
from jarray import array
from java.io import FileInputStream
from javax.net.ssl import X509ExtendedKeyManager
from net.grinder.script import Test
from net.grinder.script.Grinder import grinder
from org.italiangrid.srm.client import SRMClient, SRMClientFactory
import mkdir, rmdir, ls
import random
import string
import time
import traceback
import uuid
import os


## This loads the base properties inside grinder properties
## Should be left at the top of the script execution
load_common_properties()

error          = grinder.logger.error
info           = grinder.logger.info
debug          = grinder.logger.debug

props          = grinder.properties

# Proxy authorized to write on SRM/WEBDAV endpoints
PROXY_FILE      = get_proxy_file_path()

# Get common variables:
TEST_STORAGEAREA = props['common.test_storagearea']

## Endpoints
FRONTEND_ENDPOINT = "https://%s:%s" % (props['common.frontend_host'],props['common.frontend_port'])
SRM_ENDPOINT    = "srm://%s:%s" % (props['common.frontend_host'],props['common.frontend_port'])

# Test specific variables
TEST_DIRECTORY  = props['mkrmdir.test_directory']

SRM_SUCCESS     = TStatusCode.SRM_SUCCESS

SRM_CLIENT      = SRMClientFactory.newSRMClient(FRONTEND_ENDPOINT,PROXY_FILE)


def status_code(resp):

    return resp.returnStatus.statusCode

def explanation(resp):

    return resp.returnStatus.explanation

def check_success(res, msg):

    if status_code(res) != SRM_SUCCESS:
        error_msg = "%s. %s (expl: %s)" % (msg, status_code(res), explanation(res))
        raise Exception(error_msg)

def create_test_directory_if_needed(SRM_client):

    test_dir_surl = "%s/%s/%s" % (SRM_ENDPOINT, TEST_STORAGEAREA, TEST_DIRECTORY)
    SRM_client.srmMkdir(test_dir_surl)

def setup(SRM_client):

    info("Setting up mkrmdir test.")
    create_test_directory_if_needed(SRM_client)
    info("mkrmdir setup completed successfully.")

def mkrmdir(client):

    dir_name = str(uuid.uuid4());
    surl = "%s/%s/%s/%s" % (SRM_ENDPOINT, TEST_STORAGEAREA, TEST_DIRECTORY, dir_name)

    mkdir_runner = mkdir.TestRunner()
    mkdir_res = mkdir_runner(surl, client)
    check_success(mkdir_res, "MkDir failure on surl: %s" % surl)

    ls_runner = ls.TestRunner()
    ls_res = ls_runner(surl, client)
    check_success(ls_res, "Ls failure on surl: %s" % surl)

    rmdir_runner = rmdir.TestRunner()
    rmdir_res = rmdir_runner(surl, client)
    check_success(rmdir_res, "RmDir failure on surl: %s" % surl)


class TestRunner:

    def __call__(self):

        try:
            test = Test(TestID.MKRMDIR, "StoRM MkDir+RmDir")
            test.record(mkrmdir)

            setup(SRM_CLIENT)
            mkrmdir(SRM_CLIENT)

        except Exception, e:
            error("Error executing mkdir-rmdir: %s" % traceback.format_exc())
            raise
