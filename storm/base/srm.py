from net.grinder.script.Grinder import grinder
from gov.lbl.srm.StorageResourceManager import TStatusCode
import mkdir, rmdir, rm, ptg, sptg, ptp, sptp, rf, pd, ls

logger = grinder.logger.debug

DEFAULT_SLEEP_THRESHOLD = 50
DEFAULT_SLEEP_TIME = 0.5
WAITING_STATES  = [TStatusCode.SRM_REQUEST_QUEUED, TStatusCode.SRM_REQUEST_INPROGRESS]

def log_result_file_status(response):

    statuses = response.getArrayOfFileStatuses().getStatusArray()
    logger("surl(s) statuses:")
    for s in statuses:
        surl_attr_names = ["sourceSURL", "SURL", "surl"]
        fn = [ x for x in surl_attr_names if x in dir(s) ]
        if len(fn) == 0:
            raise Exception("SURL access methods %s not found in %s: %s" % (s,surl_attr_names,dir(s)))
        surl = getattr(s, fn[0])
        logger("%s -> %s" % (surl, s.getStatus().getStatusCode()))

def get_surl(endpoint, path):

    return "srm://%s/%s" % (endpoint, path)

def print_srm_op(operation, response):
    
    logger("%s returned status: %s (expl: %s)" % (operation, response.returnStatus.statusCode, response.returnStatus.explanation))

def check_success(response, success_status=None):
    
    if success_status is None:
        success_status = TStatusCode.SRM_SUCCESS

    res_code = response.returnStatus.statusCode
    res_expl = response.returnStatus.explanation
    if res_code != success_status:
        raise Exception("Operation failed with %s (expl: %s)" % (res_code, res_expl))

def srmMkDir(client, surl):

    mkdir_runner = mkdir.TestRunner()
    response = mkdir_runner(surl, client)
    print_srm_op("mkdir", response)
    return response

def srmRmDir(client, surl):
        
    rmdir_runner = rmdir.TestRunner()
    response = rmdir_runner(surl, client, 1)
    print_srm_op("rmdir", response)
    return response

def srmRm(client, surls):

    rm_runner = rm.TestRunner()
    response = rm_runner(surls, client)
    print_srm_op("rm", response)
    log_result_file_status(response)
    return response

def srmStatusPtG(client, ptg_response):
    
    sptg_runner = sptg.TestRunner()
    response = sptg_runner(ptg_response, client)
    print_srm_op("sptg", response)
    log_result_file_status(response)
    return response

def srmPtG(client, surls, transfer_protocols, is_sync=None, sleep_threshold=None, sleep_time=None):

    if is_sync is None:
        is_sync = True
    
    if sleep_threshold is None:
        sleep_threshold = DEFAULT_SLEEP_THRESHOLD
    
    if sleep_time is None:
        sleep_time = DEFAULT_SLEEP_TIME

    ptg_runner = ptg.TestRunner()
    ptg_response = ptg_runner(surls, transfer_protocols, client)
    print_srm_op("ptg", ptg_response)
    token = ptg_response.requestToken
    if is_sync:
        counter = 0
        while True:
            response = srmStatusPtG(client, ptg_response)
            status_code = response.returnStatus.statusCode
            counter += 1
            if status_code not in WAITING_STATES:
                break
            else:
                if counter > sleep_threshold:
                    logger("Going to sleep for %d seconds" % sleep_time)
                    time.sleep(sleep_time)
        logger("SPTG result (after %d invocations): %s: %s" % (counter, status_code, response.returnStatus.explanation))
        log_result_file_status(response)
    return (token, response)

def get_turl(status_response):
    
    return str(status_response.getArrayOfFileStatuses().getStatusArray(0).getTransferURL())

def srmRf(client, surl, token):

    rf_runner = rf.TestRunner()
    response = rf_runner(surl, token, client)
    print_srm_op("rf", response)
    return response

def srmLs(client, surl):

    ls_runner = ls.TestRunner()
    response = ls_runner(surl, client)
    print_srm_op("ls", response)
    return response

def srmStatusPtP(client, ptp_response):

    sptp_runner = sptp.TestRunner()
    response = sptp_runner(ptp_response, client)
    print_srm_op("sptp", response)
    log_result_file_status(response)
    return response

def srmPtP(client, surls, transfer_protocols, is_sync=None, sleep_threshold=None, sleep_time=None):

    if is_sync is None:
        is_sync = True

    if sleep_threshold is None:
        sleep_threshold = DEFAULT_SLEEP_THRESHOLD
    
    if sleep_time is None:
        sleep_time = DEFAULT_SLEEP_TIME

    ptp_runner = ptp.TestRunner()
    ptp_response = ptp_runner(surls, transfer_protocols, client)
    print_srm_op("ptp", ptp_response)
    token = ptp_response.requestToken
    if is_sync:
        counter = 0
        while True:
            response = srmStatusPtP(client, ptp_response)
            status_code = response.returnStatus.statusCode
            counter += 1
            if status_code not in WAITING_STATES:
                break
            else:
                if counter > sleep_threshold:
                    logger("Going to sleep for %d seconds" % sleep_time)
                    time.sleep(sleep_time)
        logger("SPTP result (after %d invocations): %s: %s" % (counter, status_code, response.returnStatus.explanation))
        log_result_file_status(response)
    return (token, response)

def srmPd(client, surls, token):

    pd_runner = pd.TestRunner()
    response = pd_runner(surls, token, client)
    print_srm_op("pd", response)
    log_result_file_status(response)
    return response
