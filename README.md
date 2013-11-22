# Grinder load  testsuite

## Setup

Download [The Grinder](http://sourceforge.net/projects/grinder/) and install it wherever you prefer, then change facility scripts under the bin directory
accordingly to your installation.  

For more information [The Grinder](http://sourceforge.net/projects/grinder/) on see [this documentation page](http://grinder.sourceforge.net/g3/getting-started.html#howtostart).

## STORM load tests test suite

Load tests for StoRM are under the storm directory.

### Available tests

* **PtG** 
* **AtlasRenaming** tests the WebDAV file renaming algorithm used by Atlas, see [details](https://github.com/italiangrid/grinder-load-testsuite/tree/master/storm/AtlasRenaming)
* **ls** execute an [srmLs](https://sdm.lbl.gov/srm-wg/doc/SRM.v2.2.html#_Toc241633105), see [details](https://github.com/italiangrid/grinder-load-testsuite/tree/master/storm/ls) 

### Executing tests

To understand how tests are executed some familiarity with [The Grinder architecture](http://grinder.sourceforge.net/g3/getting-started.html) is needed.

Grinder tests can be run alone by an [agent](http://grinder.sourceforge.net/g3/agents-and-workers.html#agent-processes) or multiple agents, possibly running different tests, can be orchestrated using the  [console](http://grinder.sourceforge.net/g3/console.html).

In order to start a single load tests see each tests instructions and run the agent as follows

    ./bin/runAgent.sh

In order to start an agent that will be controlled by the console, first edit the properties file of the test that the agent will run to set the console information
  
    # set runs to O when using this test with the console
    grinder.runs = 0
    
    grinder.useConsole = true
    grinder.consoleHost = lapventuri.cnaf.infn.it
    #grinder.consolePort = consolePort
  
In order to start the console you can use the helper script

    ./bin/runConsole.sh


### Write new tests

[Grinder tests](http://grinder.sourceforge.net/g3/scripts.html) are written using Jython, so a basic understanding of the language is needed.

Have a look at existing tests, for example [this one](https://github.com/italiangrid/grinder-load-testsuite/blob/master/storm/ls/test/test.py). That should be enough to get you started.

#### Using the SRM interface

For tests that use the SRM interface we have developed a small Java [API](https://github.com/italiangrid/test-srm-client) that is included in the testsuite libs and can be used from inside test scripts. SRM operations are exposed via [this class](https://github.com/italiangrid/test-srm-client/blob/master/src/main/java/org/italiangrid/srm/client/SRMClient.java). Currently not all operations are available, but we keep adding them as we write more tests.
