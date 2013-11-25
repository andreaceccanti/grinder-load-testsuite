# Load test for SRM rm

*Only works for one agent, one process so far.*

This test suppose the service under stand test contains directories _d1_, _d2_, .., _dn_, with _n_ less or equal to the the number of threads (which is controlled by the _grinder.threads_ property in the _test.properties_ file). Each directory is supposed to contain files _f1_, _f2_, .., _fm_ where _m_ is the value of the _storm.rm.num\_files_ property in _test.properties_). For creating this files you can use the _fixture.sh_ script in the _bin_ directory, editing the script to change the _num\_dir_ and _num\_files_ variable according to the how the test will be executed.

Edit the properties file under _storm/ls_ providing the endpoint of the service to test and other information, and run either using the runAgent script in the bin directory or directly using

	java -cp /opt/grinder-3.11/lib/*:lib/* net.grinder.Grinder storm/ls/test.properties

(this suppose grinder is installed in /opt/grinder-3.11, change according to your installation).
