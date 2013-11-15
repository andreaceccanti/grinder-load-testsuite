# Grinder load  testsuite

## Setup

Download [The Grinder](http://sourceforge.net/projects/grinder/) and install it wherever you prefer.
Scripts for environment settings are provided. Change file "bin/setupEnv.sh" accordingly with your installation.  
For more information see [this documentation page](http://grinder.sourceforge.net/g3/getting-started.html#howtostart).

## STORM load tests test suite

## Execution

In order to start the load tests run the agent as follows

    ./bin/runAgent.sh

## Tests

* **PtG** 
* **AtlasRenaming** : tests the WebDAV file renaming algorithm used by Atlas

#### PtG

#### AtlasRenaming

**setup**:

This test needs soe files to rename as input environment. To upload n files into a VO through the StoRM WebDAV interface you can use the bash script in _utils_:

	cd storm/AtlasRenaming/utils
	sh uploader.sh <webdav-hostname> <vo> <n>

It will upload _n_ files into /VO/stress-test/atlasrenaming/input directory.

**launch**:

From testsuite root directory:

	./bin/runAgent.sh ./storm/AtlasRenaming/test.properties

The moved files can be found into /VO/stress-test/atlasrenaming/output directory.
Note that:

* you can't run again the test if you don't recover the input environment before;
* you can't set _grinder.runs=0_ because if you have 100 test files, you can run one process with 5 threads for 20 runs, for example.