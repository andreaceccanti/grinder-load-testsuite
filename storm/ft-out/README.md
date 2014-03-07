# The File-Transfer-Out test

## Create a valid voms proxy 

This test requires that you have a valid voms proxy
that will be authorized to write on the storage area
specified by the `ftout.test_storagearea` property. 
Check if the environment variable X509\_USER\_PROXY exists
and contains the correct path of your VOMS proxy. 

## Set the correct endpoints

This test needs to know the srm endpoint:

```properties
ftout.frontend_host = 
ftout.frontend_port = 8444
```

and the file-transfer service endpoint:

```properties
ftout.gridhttps_host = 
ftout.gridhttps_ssl_port = 8443
```

Edit the `storm/ft-out/test.properties` file and set 
these properties as you need.

## Run the grinder console

This test requires the Grinder console to run, so start
the console using the following command:

    ./bin/runConsole.sh

## Run the agents

Once you have the console running, the proxy created and 
the test variables configured, run the agents and point
them to the host where the console is running, using the
following command:

```bash
GRINDER_USE_CONSOLE=true GRINDER_CONSOLE_HOST=host.cnaf.infn.it \
GRINDER_PROCESSES=5 GRINDER_THREADS=10 GRINDER_RUNS=50 \
./bin/runAgent.sh storm/ft-out/test.properties
```

The command above starts a local agent which connects to a 
console running on `host.cnaf.infn.it` and, when started from
the console, will run 5 processes each executing 10 threads 
of the file-transfer-out test for 50 runs.

You can run the above command on several machines in order
to have several load injectors which will be controlled 
by the console.