from common import Utils, TestID
from net.grinder.script import Test
from net.grinder.script.Grinder import grinder
from org.apache.jackrabbit.webdav import DavException
import string
import os
import uuid
import http_put, head, move, mkcol, delete

error          = grinder.logger.error
info           = grinder.logger.info
debug          = grinder.logger.debug

props          = grinder.properties

utils          = Utils(grinder.properties)

# Common variables:
TEST_STORAGEAREA = props['common.test_storagearea']

# Test specific variables
TEST_DIRECTORY = props["atlas_ren.test_directory"]
NUM_BYTES = int(props['atlas_ren.num_bytes_transferred'])

def getUniqueName():
    
    return str(uuid.uuid4());

def check_http_success(statusCode, expected_code, error_msg):
    
    if (statusCode != expected_code):
        msg = "%s. Status code is %s instead of %s" % (error_msg, statusCode, expected_code)
        raise Exception(msg)

def get_base_dir():

    return "%s/%s" % (TEST_STORAGEAREA, TEST_DIRECTORY)

def create_test_dir():

    endpoint, client = utils.get_dav_client()
    mkcol_runner = mkcol.TestRunner()
    info("Creating remote test directory ... " + get_base_dir())
    try:
        mkcol_runner(get_URL(endpoint, get_base_dir()), client)
    except DavException:
        debug("Error executing MKCOL: %s" % get_base_dir())

def create_local_file_to_upload():
    
    file_name = getUniqueName()
    file_path = "/tmp/%s" % file_name;
    debug("Creating local file to upload '%s'..." % file_path)
    file = open(file_path, "w")
    print >> file, "x" * NUM_BYTES
    file.close()
    debug("Local file created!")
    return file_path

def setup(local_file_path):

    debug("Setting up atlas renaming test.")

    endpoint, client = utils.get_dav_client()
    mkcol_runner = mkcol.TestRunner()
    http_put_runner = http_put.TestRunner()

    test_dir = "%s/%s" % (get_base_dir(), str(uuid.uuid4()))
    info("Creating specific test dir: " + test_dir)
    mkcol_runner(get_URL(endpoint, test_dir), client)

    file_name = str(uuid.uuid4())
    file_path = "%s/%s" % (test_dir, file_name)
    statusCode = http_put_runner(get_URL(endpoint, file_path), local_file_path, client)
    check_http_success(statusCode, 201, "Error in HTTP PUT")
    
    dir_level1 = "%s/%s" % (test_dir, str(uuid.uuid4()))
    dir_level2 = "%s/%s" % (dir_level1, str(uuid.uuid4()))    
    dest_file = "%s/%s" % (dir_level2, file_name)
    
    debug("test_dir = %s " % test_dir)
    debug("file_path = %s" % file_path)
    debug("dir_level1 = %s" % dir_level1)
    debug("dir_level2 = %s" % dir_level2)
    debug("dest_file = %s" % dest_file)

    debug("Atlas renaming setup completed succesfully.")
    return test_dir, file_path, dest_file, dir_level1, dir_level2

def cleanup(test_dir, local_file_path):

    debug("Cleaning up for Atlas renaming.")
    endpoint, client = utils.get_dav_client()
    delete_runner = delete.TestRunner()
    delete_runner(get_URL(endpoint, test_dir), client)
    os.remove(local_file_path)
    debug("Atlas renaming cleanup completed succesfully.")

def get_URL(endpoint, path):
	
    return "https://%s/%s" % (endpoint, path)

def atlas_renaming(src_file, dest_file, dir_l1, dir_l2):
    
    debug("Renaming "+ src_file + " to " + dest_file)
    endpoint, client = utils.get_dav_client()

    head_runner = head.TestRunner()
    head_runner(get_URL(endpoint, src_file), client)
    head_runner(get_URL(endpoint, dest_file), client)
    head_runner(get_URL(endpoint, dir_l2), client)
    head_runner(get_URL(endpoint, dir_l1), client)

    mkcol_runner = mkcol.TestRunner()
    mkcol_runner(get_URL(endpoint, dir_l1), client)
    mkcol_runner(get_URL(endpoint, dir_l2), client)

    move_runner = move.TestRunner()
    move_runner(get_URL(endpoint, src_file), get_URL(endpoint, dest_file), client)

    debug("Finished renaming file"+ src_file + " to " + dest_file)

class TestRunner:

    def __init__(self):
    
        create_test_dir()

    def __call__(self):        

        test = Test(TestID.ATLAS_RENAMING, "Atlas renaming")
        test.record(atlas_renaming)

        local_file_path = create_local_file_to_upload()
        (test_dir, src_file, dest_file, dir_level1, dir_level2) = setup(local_file_path)

        atlas_renaming(src_file, dest_file, dir_level1, dir_level2)

        cleanup(test_dir, local_file_path)
