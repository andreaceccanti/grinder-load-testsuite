# The Atlas renaming test

## Prepare the files for the renaming test

To run this test first setup the files for the test
using the script provided in [here][setup-script].

Note that this setup phase depends on how many grinder
agents you will run after, so read through the whole
procedure before creating the files.

## Create a valid voms proxy 

This test requires that you have a valid voms proxy
that will be authorized to write on the storage area
where you run the setup script. Edit the 
`storm/base/common.properties` file and set the 
`client.proxy` property to let the testsuite
know which proxy should be used:

```properties
client.proxy=/tmp/x509up_u501
```

## Run the grinder console

This test requires the Grinder console to run, so start
the console using the following command:

    ./bin/runConsole.sh

## Run the agents

Once you have the console running, the files prepared and
the proxy created and configured, run the agents and point
them to the host where the console is running, using the
following command:

```bash
GRINDER_USE_CONSOLE=true GRINDER_CONSOLE_HOST=host.cnaf.infn.it \
GRINDER_PROCESSES=5 GRINDER_THREADS=10 GRINDER_RUNS=50 \
./bin/runAgent.sh storm/atlas-renaming-no-setup/test.properties
```

The command above starts a local agent which connects to a 
console running on `host.cnaf.infn.it` and, when started from
the console, will run 5 processes each executing 10 threads 
of the atlas-renaming-no-setup test for 50 runs.

You can run the above command on several machines in order
to have several load injectors which will be controlled 
by the console.

Note that after each test run you will need to:

- recreate the files 
- stop the agents from the console and restart them

[setup-script]: https://gist.github.com/andreaceccanti/bb7a3c3f58577724be4b
