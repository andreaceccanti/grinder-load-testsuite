from java.util import Properties
from java.io import FileInputStream, BufferedInputStream
from net.grinder.script.Grinder import grinder
from org.italiangrid.srm.client import SRMClientFactory
from org.italiangrid.dav.client import WebDAVClient, WebDAVClientFactory
from org.slf4j import Logger, LoggerFactory
import os
import random


class Utils:
    
    def __init__(self, props):
        self.props = props
        self.is_init_srm_clients = False
        self.is_init_dav_clients = False

    def init_srm_clients(self):
        
        if self.is_init_srm_clients:
            return
        
        self.srm_clients = []
        frontends = [f.strip() for f in self.get_storm_fe_endpoint_list().split(',')]
        for f in frontends:
            client = SRMClientFactory.newSRMClient("https://%s" % f, self.get_proxy_file_path())
            self.srm_clients.append((f,client))
        self.is_init_srm_clients = True
        
    def init_dav_clients(self):
        
        if self.is_init_dav_clients:
            return
        
        self.dav_clients = []
        davs = [dav.strip() for dav in self.get_storm_dav_endpoint_list().split(',')]
        for dav in davs:
            client = WebDAVClientFactory.newWebDAVClient("https://%s" % dav, self.get_proxy_file_path())
            self.dav_clients.append((dav,client))
        self.is_init_dav_clients = True
        
    def get_proxy_file_path(self):

        uid = os.geteuid()
        if uid is "0":
            raise Exception("root user is not allowed!")
        return os.getenv('X509_USER_PROXY', "/tmp/x509up_u%s" % uid)
    
    def get_storm_be_hostname(self):

        be_host = self.props["common.storm_be_hostname"]
        if be_host is None:
            raise Exception("Missed common.storm_be_hostname value")        
        return be_host
    
    def get_storm_fe_endpoint_list(self):
        
        fe_list = self.props["common.storm_fe_endpoint_list"]
        if fe_list is None:
            raise Exception("Missed common.storm_fe_endpoint_list value")
        return fe_list
    
    def get_storm_dav_endpoint_list(self):
        
        dav_list = self.props["common.storm_dav_endpoint_list"]
        if dav_list is None:
            raise Exception("Missed common.storm_dav_endpoint_list value")
        return dav_list

    def get_srm_client(self):
        
        self.init_srm_clients()
        return random.choice(self.srm_clients)

    def get_dav_client(self):
        
        self.init_dav_clients()
        return random.choice(self.dav_clients)


def get_surl(endpoint, storagearea, path):
    
    return "srm://%s/%s/%s" % (endpoint, storagearea, path)

def get_url(protocol, endpoint, storagearea, path):
    
    return "%s://%s/webdav/%s/%s" % (protocol, endpoint, storagearea, path)   

def get_logger(name):
    
    return LoggerFactory.getLogger(name)

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
