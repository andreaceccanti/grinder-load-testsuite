from common import TestID, load_common_properties
from eu.emi.security.authn.x509.impl import PEMCredential
from net.grinder.script import Test
from net.grinder.script.Grinder import grinder
from org.italiangrid.srm.client import SRMClient, SRMClientFactory
from org.italiangrid.dav.client import WebDAVClient, WebDAVClientFactory
from gov.lbl.srm.StorageResourceManager import TStatusCode
import random
import string
import os
import commands
import traceback
import uuid
import time
import mkdir, http_put, head, move, mkcol, rmdir

# this loads the base properties inside grinder properties
load_common_properties()

error          = grinder.logger.error
info           = grinder.logger.info
debug          = grinder.logger.debug

props          = grinder.properties

PROXY_FILE     = props['client.proxy']

MULTIHEAD_HOST = props['multi_head.host']
MULTIHEAD_PORT = props['multi_head.port']
MULTIHEAD_COUNT = int(props['multi_head.count'])

MULTIHEAD_ENDPOINT = "https://" + MULTIHEAD_HOST + ":" + MULTIHEAD_PORT

def status_code(resp):
    return resp.returnStatus.statusCode

def explanation(resp):
    return resp.returnStatus.explanation

def multi_head(client):

    head_runner = head.TestRunner()
    for i in range(MULTIHEAD_COUNT):
        head_runner("/f"+i, client)

class TestRunner:

    def __call__(self):

        test = Test(TestID.MULTI_HEAD, "Multi head test")
        test.record(multi_head)

        debug("MULTIHEAD_ENDPOINT: %s" % MULTIHEAD_ENDPOINT)

        http_client = WebDAVClientFactory.newWebDAVClient(MULTIHEAD_ENDPOINT, PROXY_FILE)

        multi_head(http_client)
