from common import *
from srm import *
from exceptions import Exception
from jarray import array
from java.io import FileInputStream
from net.grinder.script import Test
from net.grinder.script.Grinder import grinder
import random
import string
import traceback
import uuid
import os

error          = grinder.logger.error
info           = grinder.logger.info
debug          = grinder.logger.debug

props          = grinder.properties

utils          = Utils(grinder.properties)

# Get common variables:
TEST_STORAGEAREA = props['common.test_storagearea']

# Test specific variables
TEST_DIRECTORY  = props['mkrmdir.test_directory']

def get_base_dir():
    
    return "%s/%s" % (TEST_STORAGEAREA, TEST_DIRECTORY)

def setup():

    info("Setup mkrmdir test ...")
    endpoint, client = utils.get_srm_client()
    info("Creating remote test directory ... " + get_base_dir())
    srmMkDir(client, get_surl(endpoint, get_base_dir()))
    info("mkrmdir setup completed successfully.")

def mkrmdir():

    debug("Make/Remove directory started")
    endpoint, client = utils.get_srm_client()
    dir_name = str(uuid.uuid4());
    dir_path = "%s/%s/%s" % (TEST_STORAGEAREA, TEST_DIRECTORY, dir_name)
    surl = get_surl(endpoint, dir_path)
    response = srmMkDir(client, surl)
    info("MK-DIR %s - [%s %s]" % (surl, response.returnStatus.statusCode, response.returnStatus.explanation))
    check_success(response)
    response = srmRmDir(client, surl)
    info("RM-DIR %s - [%s %s]" % (surl, response.returnStatus.statusCode, response.returnStatus.explanation))
    check_success(response)
    debug("Make/Remove directory finished")


class TestRunner:
    
    def __init__(self):

        setup()

    def __call__(self):

        try:
            test = Test(TestID.MKRMDIR_TEST, "StoRM MkDir+RmDir")
            test.record(mkrmdir)
            mkrmdir()

        except Exception, e:
            error("Error executing mkdir-rmdir: %s" % traceback.format_exc())
            raise
