from net.grinder.script.Grinder import grinder
import random, string
import ptp
import pd
import rm
import tin

# aliases for grinder stuff
props = grinder.properties
log = grinder.logger.info

# test parameters as fetched from grinder.properties
FE_HOST = props['storm.host']
BASE_FILE_PATH=props['storm.base_file_path']

# computed vars
SRM_ENDPOINT = "https://%s" % FE_HOST
SURL_PREFIX="srm://%s/%s" % (FE_HOST, BASE_FILE_PATH)

class TestRunner:

	# this method is called for every run
	def __call__(self):

		surl = SURL_PREFIX + "/" + ''.join(random.choice(string.lowercase) for i in range(4))
		surls = []
		surls.append(surl)

		ptpTestRunner = ptp.TestRunner()
		res = ptpTestRunner(surls)

		tinTestRunner = tin.TestRunner()
		tinTestRunner(res.getArrayOfFileStatuses().getStatusArray(0).getTransferURL())

		pdTestRunner = pd.TestRunner()
		pdTestRunner(surls, res.getRequestToken())

		rmTestRunner = rm.TestRunner()
		rmTestRunner(surls)
