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
import mkdir, ptp, sptp, pd, ls, rmdir
import random
import string
import time
import traceback
import uuid
import os

# Test: create width x height elements, save surls and ls one element random each run

error          = grinder.logger.error
info           = grinder.logger.info
debug          = grinder.logger.debug

props          = grinder.properties

conf           = Configuration()
utils          = Utils()

# Get common variables:
SRM_CLIENTS = utils.get_srm_clients(conf)
TEST_STORAGEAREA = conf.get_test_storagearea()

# Test specific variables
TEST_DIRECTORY  = props['ls.test_directory']
TEST_DIR_WIDTH  = int(props['ls.test_directory_width'])
TEST_DIR_HEIGHT = int(props['ls.test_directory_height'])

DO_SETUP        = props['ls.do_setup']
DO_CLEANUP      = props['ls.do_cleanup']

DIRECTORY_NAME  = "testdir"
FILE_PREFIX  = "file"

SRM_SUCCESS     = TStatusCode.SRM_SUCCESS
WAITING_STATES  = [TStatusCode.SRM_REQUEST_QUEUED, TStatusCode.SRM_REQUEST_INPROGRESS]

def get_client():
    return random.choice(SRM_CLIENTS)

TEST_DIRECTORY_SURL = utils.get_surl(get_client()[0], TEST_STORAGEAREA, TEST_DIRECTORY)

def initSURLs():
    surls = []
    current = TEST_DIRECTORY_SURL
    for i in range(1, TEST_DIR_HEIGHT + 1):
        next = "%s/%s" % (current, DIRECTORY_NAME)
        surls.append(next)
        debug("appended: %s" % next)
        current = next
    return surls

SURLS = initSURLs()

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

def upload_file(client, surl):
    debug("Upload file %s" % surl)
    # create runners
    ptp_runner = ptp.TestRunner()
    sptp_runner = sptp.TestRunner()
    pd_runner = pd.TestRunner()
    # ptp
    res = ptp_runner([surl], [], client)
    while True:
        # sptp
        sres = sptp_runner(res, client)
        if status_code(sres) in WAITING_STATES:
            time.sleep(1)
        else:
            break
    check_success(sres, "Error in PtP for surl: %s." % surl)
    # pd
    res = pd_runner([surl], res.requestToken, client)
    check_success(res, "Error in PD for surl: %s" % surl)
    debug("File %s successfully uploaded." % surl)

def generateTree(client):
    info("Creating test directories and files")
    for dsurl in SURLS:
        create_directory(client, dsurl)
        for j in range(1, TEST_DIR_WIDTH + 1):
            fsurl = "%s/%s_%d" % (dsurl, FILE_PREFIX, j)
            upload_file(client, fsurl)

def setup():
    info("Setting up ls test.")
    client = get_client()[1]
    create_directory(client, TEST_DIRECTORY_SURL)
    generateTree(client)
    info("ls setup completed successfully.")

def cleanup():
    info("Cleaning up ls test main dir: %s" % SURLS[0])
    rmdir_runner = rmdir.TestRunner()
    res = rmdir_runner(SURLS[0], get_client()[1], 1)
    check_success(res, "Error in rmDir for surl: %s" % SURLS[0])
    info("ls cleanup completed successfully.")

def ls_test(surl):
    ls_runner = ls.TestRunner()
    ls_res = ls_runner(surl, get_client()[1])
    check_success(ls_res, "Ls failure on surl: %s" % surl)


class TestRunner:

    def __init__(self):
        self.SetupCompleteBarrier = grinder.barrier("Init barrier")
        self.ReadyToCleanUpBarrier = grinder.barrier("Cleanup barrier")
        self.numruns = int(props["grinder.runs"])

    def __call__(self):
        
        if ((DO_SETUP == "yes") and (self.isFirstRun())):
            if (self.isTheInitializer()):
                cleanup()
                setup()
            debug("waiting all the other threads")
            self.SetupCompleteBarrier.await()
            debug("ok, go!")

        try:
            test = Test(TestID.LS_TEST, "StoRM LS test")
            test.record(ls_test)
            i = random.randint(1, TEST_DIR_HEIGHT) - 1
            info("[i = %d] Ls on %s" % (i, SURLS[i]))
            ls_test(SURLS[i])
        except Exception, e:
            error("Error executing ls test: %s" % traceback.format_exc())
            raise

        if ((DO_CLEANUP == "yes") and (self.isLastRun())):
            debug("waiting all the other threads")
            self.ReadyToCleanUpBarrier.await()
            debug("ok, ready to cleanup!")
            if (self.isTheInitializer()):
                 cleanup()

    def isFirstRun(self):
        return grinder.getRunNumber() == 0

    def isLastRun(self):
        return grinder.getRunNumber() == (self.numruns - 1)

    def getId(self):
        agent = grinder.getAgentNumber()
        process = grinder.getProcessNumber()
        thread = grinder.getThreadNumber()
        debug("I'm A:%s,P:%s,T:%s" % (agent,process,thread))
        if (agent == -1):
            return process + thread
        return agent + process + thread

    def isTheInitializer(self):
        id = self.getId()
        debug("My id is %s" % id)
        return id == 0