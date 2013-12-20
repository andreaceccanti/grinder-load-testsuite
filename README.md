# Grinder load  testsuite

## Setup

Download [The Grinder](http://sourceforge.net/projects/grinder/) and install it
wherever you prefer.

We usually install it in `/opt/grinder-3.11/` but any place is fine,
provided that you then export the location as follows:

````bash
export GRINDER_HOME="/opt/grinder-3.11"
```

For more information on [The Grinder](http://sourceforge.net/projects/grinder/)
see [this documentation page](http://grinder.sourceforge.net/g3/getting-started.html#howtostart).

## STORM load tests test suite

Load tests for StoRM are under the storm directory.

## Running tests

To understand how tests are executed some familiarity with [The Grinder
architecture](http://grinder.sourceforge.net/g3/getting-started.html) is needed.

Grinder tests can be run alone by an
[agent](http://grinder.sourceforge.net/g3/agents-and-workers.html#agent-processes)
or multiple agents, possibly running different tests, can be orchestrated using
the  [console](http://grinder.sourceforge.net/g3/console.html).

For details on how to run tests check the 

    ./bin/runAgent.sh

test run script.

A convenience script to run the grinder console is also provided:

    ./bin/runConsole.sh

### Write new tests

[Grinder tests](http://grinder.sourceforge.net/g3/scripts.html) are written
using Jython, so a basic understanding of the language is needed.

Have a look at existing tests, for example [this
one](https://github.com/italiangrid/grinder-load-testsuite/blob/master/storm/ls/test/test.py).
That should be enough to get you started.

#### Using the SRM interface

For tests that use the SRM interface we have developed a small Java
[API](https://github.com/italiangrid/test-srm-client) that is included in the
testsuite libs and can be used from inside test scripts. SRM operations are
exposed via [this
class](https://github.com/italiangrid/test-srm-client/blob/master/src/main/java/org/italiangrid/srm/client/SRMClient.java).
Currently not all operations are available, but we keep adding them as we write
more tests.


