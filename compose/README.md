# StoRM load testsuite

## Configure tests through environment

Environment variables:

| Name | Description | Default
|------|-------------|--------
| TESTSUITE_REPO 	 | URL of the grinder testsuite git repository | git://github.com/italiangrid/grinder-load-testsuite.git
| TESTSUITE\_BRANCH  | Which branch of TESTSUITE\_REPO use | develop
| PROXY\_VONAME      | The test VO for which a VOMS-proxy will be asked. Values: test.vo, test.vo.2 | test.vo
| PROXY\_USER 		 | The test VO user credentials to use | test0
| GRINDER\_PROCESSES | Number of processes to run | 1
| GRINDER\_THREADS	 | Number of process' threads to run | 1
| GRINDER\_RUNS 	 | Number of test executions for each thread | 1
| GRINDER\_CONSOLE\_USE		| Boolean value used to activate the use of a Grinder console. Values: true, false | false
| GRINDER\_CONSOLE\_HOST	| In case console is enabled, this is its hostname | localhost
| GRINDER\_TEST				| The test that has to be run. Read table below. | mixdav
| COMMON\_STORM\_FE\_ENDPOINT\_LIST	  | Comma separated list of FE end-points in form HOSTNAME:PORT | omii006-vm03.cnaf.infn.it:8444
| COMMON\_STORM\_DAV\_ENDPOINT\_LIST  | Comma separated list of WebDAV secured end-points in form HOSTNAME:PORT | omii006-vm03.cnaf.infn.it:8443
| COMMON\_TEST\_STORAGEAREA		| Test VO storage area's access point | test.vo
| LOGGING\_LEVEL 				| Sets the grinder worker nodes logging level | INFO

Test types for GRINDER\_TEST:

| Name  | Description |
|-------|-------------|
| atlas_nested		|	Each thread creates `atlas_nested.nesting_levels` nested directories into remote `atlas_nested.test_directory`, and upload a file (size = `atlas_nested.file_size_in_bytes`). The test consists of one srmLs, followed by a srmPtG and a srmRf on file surl. At the end, each thread cleans its remote file.
| atlas_renaming	| WebDAV test: move a SOURCE file to a DIR1/DIR2/DESTINATION path. Operations: HEAD on SOURCE, HEAD on DESTINATION, HEAD on DIR2, HEAD on DIR1, MKCOL DIR1, MKCOL DIR2, MOVE
| ft_in				| srmPtG, HTTP GET, srmRf
| ft_out			| srmPtP, HTTP PUT, srmPd
| ls_test			| srmLs on `ls_test.num_files` files created once.
| mixdav			| MKCOL, PUT, PUT, GET, GET, MOVE, DELETE
| mkrmdir_test		| srmMkDir + srmRmDir
| ptg_test			| upload n files (setup) and then run a srmPtG + srmRf. (srmRm on cleanup)
| ptp_test			| srmPtP + srmPd + srmRm
| ptp_pd			| srmPtP + globus_url_copy + srmPd
| rm_multi			| upload n-files + single srmRm for each file
| rm_test 			| upload n-files and remove all of them with one srmRm

Run one test with compose:

	GRINDER_TEST=mkrmdir_test docker-compose up

Run never-ending tests (GRINDER_RUNS=0):

	GRINDER_TEST=mkrmdir_test GRINDER_RUNS=0 docker-compose up

Run with a provided proxy:

	cp /local/path/to/proxy ./assets/proxy
	GRINDER_TEST=mkrmdir_test GRINDER_RUNS=0 docker-compose up