import random, string
import mkdir, rmdir


class TestRunner:

	def __call__(self):

		dirname = ''.join(random.choice(string.lowercase) for i in range(8))

		mkdirTestRunner = mkdir.TestRunner()
		res = mkdirTestRunner(dirname)

		rmdirTestRunner = rmdir.TestRunner()
		rmdirTestRunner(dirname)
