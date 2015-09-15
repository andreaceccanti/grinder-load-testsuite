from common import TestID, Configuration, Utils
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

error          = grinder.logger.error
info           = grinder.logger.info
debug          = grinder.logger.debug

props          = grinder.properties

conf           = Configuration()
utils          = Utils()

# Get common variables:
SRM_CLIENTS = utils.get_srm_clients(conf)
TEST_STORAGEAREA = conf.get_test_storagearea()

# Get common variables:
TEST_STORAGEAREA = props['common.test_storagearea']

# Test specific variables
TEST_DIRECTORY  = props['mkrmdir.test_directory']

SRM_SUCCESS     = TStatusCode.SRM_SUCCESS

def get_client():
    return random.choice(SRM_CLIENTS)

TEST_DIRECTORY_SURL = utils.get_surl(get_client()[0], TEST_STORAGEAREA, TEST_DIRECTORY)

def status_code(resp):

    return resp.returnStatus.statusCode

def explanation(resp):

    return resp.returnStatus.explanation

def check_success(res, msg):

    if status_code(res) != SRM_SUCCESS:
        error_msg = "%s. %s (expl: %s)" % (msg, status_code(res), explanation(res))
        raise Exception(error_msg)

def create_directory(client, surl):
    mkdir_runner = mkdir.TestRunner()
    res = mkdir_runner(surl, client)
    debug("mkdir returned status: %s (expl: %s)" % (status_code(res), explanation(res)))

def setup():

    info("Setting up mkrmdir test.")
    client = get_client()[1] 
    create_directory(client, TEST_DIRECTORY_SURL)
    info("mkrmdir setup completed successfully.")

def mkrmdir():

    debug("Make/Remove directory started")

    client = get_client()[1]
    dir_name = str(uuid.uuid4());
    surl = "%s/%s" % (TEST_DIRECTORY_SURL, dir_name)

    mkdir_runner = mkdir.TestRunner()
    mkdir_res = mkdir_runner(surl, client)
    check_success(mkdir_res, "MkDir failure on surl: %s" % surl)

    ls_runner = ls.TestRunner()
    ls_res = ls_runner(surl, client)
    check_success(ls_res, "Ls failure on surl: %s" % surl)

    rmdir_runner = rmdir.TestRunner()
    rmdir_res = rmdir_runner(surl, client)
    check_success(rmdir_res, "RmDir failure on surl: %s" % surl)

    debug("Make/Remove directory finished")


class TestRunner:

    def __call__(self):

        try:
            test = Test(TestID.MKRMDIR, "StoRM MkDir+RmDir")
            test.record(mkrmdir)

            setup()
            mkrmdir()

        except Exception, e:
            error("Error executing mkdir-rmdir: %s" % traceback.format_exc())
            raise
