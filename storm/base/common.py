from java.util import Properties
from java.io import FileInputStream, BufferedInputStream
from net.grinder.script.Grinder import grinder
from org.italiangrid.srm.client import SRMClientFactory
from org.italiangrid.dav.client import WebDAVClient, WebDAVClientFactory
from org.slf4j import Logger, LoggerFactory
import os
import random

error           = grinder.logger.error
info            = grinder.logger.info
debug           = grinder.logger.debug

def get_logger(name):
    return LoggerFactory.getLogger(name)

class Configuration:
    
    props = grinder.properties

    def get_proxy_file_path(self):
        return os.getenv('X509_USER_PROXY', "/tmp/x509up_u%s" % os.geteuid())
    
    def get_storm_be_hostname(self):
        return os.getenv('STORM_BE_HOSTNAME', self.props["common.storm_be_hostname"])
    
    def get_storm_fe_endpoint_list(self):
        return os.getenv('STORM_FE_ENDPOINT_LIST', self.props["common.storm_fe_endpoint_list"])
    
    def get_storm_dav_endpoint_list(self):
        return os.getenv('STORM_DAV_ENDPOINT_LIST', self.props["common.storm_dav_endpoint_list"])
    
    def get_test_storagearea(self):
        return os.getenv('TESTSUITE_STORAGE_AREA', self.props["common.test_storagearea"])

    def get_prop(self, name):
        return self.props[name]   
 
class Utils:
    
    def get_srm_clients(self, conf):
        clients = []
        frontends = [f.strip() for f in conf.get_storm_fe_endpoint_list().split(',')]
        for f in frontends:
            client = SRMClientFactory.newSRMClient("https://%s" % f, conf.get_proxy_file_path())
            clients.append((f,client))
        return clients
    
    def get_dav_clients(self, conf):
        clients = []
        webdavs = [dav.strip() for dav in conf.get_storm_dav_endpoint_list().split(',')]
        for dav in webdavs:
            info("get_dav_clients: creating client on %s" % dav)
            client = WebDAVClientFactory.newWebDAVClient("https://%s" % dav, conf.get_proxy_file_path())
            clients.append((dav,client))
        return clients
    
    def get_surl(self, endpoint, storagearea, path):
        return "srm://%s/%s/%s" % (endpoint, storagearea, path)
    

def log_surl_call_result(op_name, res, logger=None):

    if logger is None:
        logger = grinder.logger.debug

    logger("%s result: %s (expl: %s)" %
           (op_name, res.returnStatus.statusCode,
            res.returnStatus.explanation))
    statuses = res.getArrayOfFileStatuses().getStatusArray()

    logger("surl(s) statuses:")
    for s in statuses:
        surl_attr_names = ["sourceSURL", "SURL", "surl"]
        fn = [ x for x in surl_attr_names if x in dir(s) ]
        if len(fn) == 0:
            raise Exception("SURL access methods %s not found in %s: %s" % (s,surl_attr_names,dir(s)))
        surl = getattr(s, fn[0])
        logger("%s -> %s" %(surl,
                            s.getStatus().getStatusCode()))



class TestID():
    PTG       = 1
    SPTG      = 2
    PTP       = 3
    SPTP      = 4
    LS        = 5
    RM        = 6
    MKDIR     = 7
    RMDIR     = 8
    MV        = 9
    RF        = 10
    HTTP_GET  = 11
    HTTP_PUT  = 12
    PD        = 13
    HEAD      = 14
    MKCOL     = 15
    MOVE      = 16
    PTP_SYNC  = 17
    DELETE    = 18

    PTG_SYNC  = 100
    PTP_SYNC_PD = 101
    TXFER_IN  = 102
    TXFER_OUT = 103
    MKRMDIR   = 104
    ATLAS_RENAMING = 105
    MULTI_HEAD = 106
    PTP_ASYNC_PD = 107
    RM_FILES  = 108
    LS_TEST   = 109
    MIX_DAV   = 110
    PTG_ASYNC = 111
    GET_DAV   = 112
    PUT_DAV   = 113
