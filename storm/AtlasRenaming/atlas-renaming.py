from common import TestID, load_common_properties
from eu.emi.security.authn.x509.impl import PEMCredential
from net.grinder.script import Test
from net.grinder.script.Grinder import grinder
from org.italiangrid.srm.client import SRMClient, SRMClientFactory
from gov.lbl.srm.StorageResourceManager import TStatusCode

import random
import string
import os
import commands
import traceback
import uuid
import time
import http_put

## This loads the base properties inside grinder properties
## Should be left at the top of the script execution
load_common_properties()

error          = grinder.logger.error
info           = grinder.logger.info
debug          = grinder.logger.debug

props          = grinder.properties


PROXY_FILE     = props['client.proxy']
BASE_FILE_PATH = props['atlas_ren.base_file_path']

VO = props['atlas_ren.vo']

# Computed vars
FE_HOST        = props['storm.host']
SRM_ENDPOINT = "https://%s" % FE_HOST
SURL_PREFIX="srm://%s/%s/%s" % (FE_HOST,VO,BASE_FILE_PATH)

WAITING_STATES = [TStatusCode.SRM_REQUEST_QUEUED, TStatusCode.SRM_REQUEST_INPROGRESS]
SRM_SUCCESS  = TStatusCode.SRM_SUCCESS

NUM_FILES=int(props['atlas_ren.num_files'])
NUM_BYTES = int(props['atlas_ren.num_bytes_transferred'])

GLOBUS_DIR=os.environ['HOME'] + '/.globus'
USERCERT=GLOBUS_DIR + '/usercert.pem'
USERKEY=GLOBUS_DIR + '/userkey.pem'

CACERTS="/etc/grid-security/certificates"

WEBDAV_HOST = props['atlas_ren.host']
WEBDAV_PORT = props['atlas_ren.port']
WEBDAV_ENDPOINT = "https://" + WEBDAV_HOST + ":" + WEBDAV_PORT + "/webdav"


class StoRMWebDAV:

	def __init__(self, endpoint):
		self._endpoint = endpoint

	def execute(self, command):
		output=commands.getoutput(command)
		return output

	def getCurlOptions(self):
		return "--cert " + PROXY_FILE + " --cacert " + USERCERT + " --capath " + CACERTS

	def getDavURL(self, vo, remotepath):
		return self._endpoint + "/" + vo + "/" + remotepath

	def doHead(self, vo, remotepath):
		return self.execute("curl " + self.getCurlOptions() + " --head " + self.getDavURL(vo, remotepath))

	def doMkCol(self, vo, remotepath):
		return self.execute("curl " + self.getCurlOptions() + " -X MKCOL " + self.getDavURL(vo, remotepath))

	def doMove(self, srcvo, srcpath, destvo, destpath):
		return self.execute("curl " + self.getCurlOptions() + " -X MOVE " + self.getDavURL(srcvo, srcpath) + " --header 'Destination:" + self.getDavURL(destvo, destpath) + "'")


def randomword(length):
	return ''.join(random.choice(string.lowercase) for i in range(length))

def status_code(resp):
    return resp.returnStatus.statusCode

def explanation(resp):
    return resp.returnStatus.explanation

def check_success(res, msg):
    if status_code(res) != SRM_SUCCESS:
        error_msg = "%s. %s (expl: %s)" % (msg, status_code(res), explanation(res))
        raise Exception(error_msg)

def compute_filename():
    random_index = random.randint(0,NUM_FILES-1)
    filename = "f%d" % (random_index)
    return filename

def setup(client):
    debug("Setting up Atlas renaming test.")
   
    id=str(uuid.uuid4())
    
    surl_base_dir = "%s/%s" % (SURL_PREFIX, id)
    debug("Creating base dir: " + surl_base_dir)
    res = client.srmMkdir(surl_base_dir)
    check_success(res, "Error creating %s" % surl_base_dir)
    debug("Base directory succesfully created.")
        
    fname=compute_filename()
    filename="%s/%s" % (surl_base_dir,fname)
    
    surls=[]
    surls.append(filename)
    
    protocols=[]
    protocols.append("http")
    
    res = client.srmPtP(surls,protocols)
    while True:
        sres = client.srmSPtP(res)
        if status_code(sres) in WAITING_STATES:
            time.sleep(1)
        else:
            break

    check_success(sres, "Error in PtP for surls (only 5 shown out of %d): %s." % (len(surls),surls[0:5]))
    
    turls = sres.getArrayOfFileStatuses().getStatusArray(0).getTransferURL()
        
    http_put_runner=http_put.TestRunner()
    put_res=http_put_runner(turls,NUM_BYTES)
    
    res = client.srmPd(surls, res.requestToken)
    check_success(res, "Error in PD for surls: %s" % surls)
    debug("Atlas renaming setup completed succesfully.")
    
    base_dir="%s/%s" % (SURL_PREFIX, id)
    webdav_basedir="%s/%s" % (BASE_FILE_PATH,id)
    dir_level1="%s/%s" % (webdav_basedir,randomword(10))
    dir_level2="%s/%s" % (dir_level1,randomword(10))    
    src_file="%s/%s" % (webdav_basedir,fname)
    dest_file="%s/%s" % (dir_level2,compute_filename())
	
    return base_dir,src_file,dest_file,dir_level1,dir_level2

def cleanup(client, base_dir):
    debug("Cleaning up for Atlas renaming.")

    res = client.srmRmdir(base_dir, True)
    if status_code(res) != SRM_SUCCESS:
        raise Exception("srmRmdir failed for %s. %s %s" %(base_dir, status_code(res), explanation(res)))
    debug("Atlas renaming cleanup completed succesfully.")

def atlas_renaming(webdav,src_file,dest_file,dir_l1,dir_l2):
		debug("Renaming file "+ src_file + " to " + dest_file)
		
		webdav.doHead(VO, src_file)
		webdav.doHead(VO, dest_file)
		webdav.doHead(VO, dir_l2)
		webdav.doHead(VO, dir_l1)
		webdav.doMkCol(VO, dir_l1)
		webdav.doMkCol(VO, dir_l2)
		webdav.doMove(VO, src_file, VO, dest_file)		
		
class TestRunner:
	def __call__(self):		
		
		test = Test(TestID.ATLAS_RENAMING, "WebDav Atlas renaming")					
		test.record(atlas_renaming)
		client = SRMClientFactory.newSRMClient(SRM_ENDPOINT,PROXY_FILE)
		
		(base_dir,src_file,dest_file,dir_level1,dir_level2)=setup(client)
		
		webdav = StoRMWebDAV(WEBDAV_ENDPOINT)
		atlas_renaming(webdav,src_file, dest_file,dir_level1,dir_level2)
		cleanup(client, base_dir)