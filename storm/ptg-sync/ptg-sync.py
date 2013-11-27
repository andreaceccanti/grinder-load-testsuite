from common import TestID, load_common_properties
from eu.emi.security.authn.x509.impl import PEMCredential
from exceptions import Exception
from gov.lbl.srm.StorageResourceManager import TStatusCode
from jarray import array
from java.io import FileInputStream
from javax.net.ssl import X509ExtendedKeyManager
from net.grinder.plugin.http import HTTPRequest
from net.grinder.script import Test
from net.grinder.script.Grinder import grinder
from org.italiangrid.srm.client import SRMClient, SRMClientFactory
import ptg
import random
import sptg
import string
import time
import traceback

## This loads the base properties inside grinder properties
## Should be left at the top of the script execution
load_common_properties()

error          = grinder.logger.error
info           = grinder.logger.info
debug          = grinder.logger.debug

props          = grinder.properties

PROXY_FILE     = props['client.proxy']
FE_HOST        = props['storm.host']
BASE_FILE_PATH = props['ptg-sync.base_file_path']

SRM_ENDPOINT   = "https://%s" % FE_HOST
SURL_PREFIX    = "srm://%s/%s" % (FE_HOST, BASE_FILE_PATH)

WAITING_STATES = [TStatusCode.SRM_REQUEST_QUEUED, TStatusCode.SRM_REQUEST_INPROGRESS]

# Start sleeping between sptg requests after this number
SLEEP_THRESHOLD = 10
## Sleep time (seconds)
SLEEP_TIME = .5

def status_code(resp):
    return resp.returnStatus.statusCode

def compute_surls():
    random_index = random.randint(1,10)
    surl = "%s/f%d" % (SURL_PREFIX,random_index)
    return [surl]

class TestRunner:
    def _run(self):
        surls = compute_surls()
        ptg_runner = ptg.TestRunner()
        ptg_res = ptg_runner(surls,[],self._client)
        sptg_runner = sptg.TestRunner()

        counter = 0

        while True:
            res =  sptg_runner(ptg_res,self._client)
            counter = counter + 1
            sc = status_code(res)
            debug("sPtG invocation %d status code: %s" % (counter,sc) )

            if sc not in WAITING_STATES:
                break
            else:
                if counter > SLEEP_THRESHOLD:
                    debug("Going to sleep for %d seconds" % SLEEP_TIME)
                    time.sleep(SLEEP_TIME)

        info("SPTG result (after %d invocations): %s: %s" %
            (counter, res.returnStatus.statusCode, res.returnStatus.explanation))

    def __call__(self):
        try:
            test = Test(TestID.PTG_SYNC, "StoRM Sync PTG test")
            test.record(self._run)
            self._client = SRMClientFactory.newSRMClient(SRM_ENDPOINT,PROXY_FILE)
            self._run()
        except Exception, e:
            error("Error executing ptg-sync: %s" % traceback.format_exc())
