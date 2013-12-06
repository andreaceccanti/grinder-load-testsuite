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
BASE_FILE_PATH = props['atlas_ren.base_file_path']

WEBDAV_HOST = props['atlas_ren.host']
WEBDAV_PORT = props['atlas_ren.port']
WEBDAV_ENDPOINT = "https://" + WEBDAV_HOST + ":" + WEBDAV_PORT

def status_code(resp):
    return resp.returnStatus.statusCode

def explanation(resp):
    return resp.returnStatus.explanation

def atlas_renaming(client):

    process_number = grinder.processNumber
    thread_number = grinder.threadNumber
    run_number = grinder.runNumber

    thread_prefix = "%s/p%d/t%d" % (BASE_FILE_PATH,
                                    process_number,
                                    thread_number)

    src_file=  "%s/f%d" % (thread_prefix, run_number)

    dir_l1 = "%s/dl1_r%d" % (thread_prefix, run_number)
    dir_l2 = "%s/dl2_r%d" % (dir_l1, run_number)

    dest_file = "%s/f%d" % (dir_l2, run_number)

    debug("Renaming %s -> %s " % (src_file,dest_file) )

    head_runner = head.TestRunner()
    head_runner(src_file, client)
    head_runner(dest_file, client)
    head_runner(dir_l2, client)
    head_runner(dir_l1, client)

    mkcol_runner = mkcol.TestRunner()
    mkcol_runner(dir_l1, client)
    mkcol_runner(dir_l2, client)

    move_runner = move.TestRunner()
    move_runner(src_file, dest_file, client)

    debug("Done renaming: %s -> %s" % (src_file, dest_file))

class TestRunner:

    def __call__(self):

        test = Test(TestID.ATLAS_RENAMING, "Atlas renaming")
        test.record(atlas_renaming)

        debug("WEBDAV_ENDPOINT: %s" % WEBDAV_ENDPOINT)

        http_client = WebDAVClientFactory.newWebDAVClient(WEBDAV_ENDPOINT, PROXY_FILE)

        atlas_renaming(http_client)
