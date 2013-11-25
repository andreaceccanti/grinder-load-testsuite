# Load test for SRM ls

This test suppose the service under test manages files named _f1__ .. _fn_ (where _n_ is the value of the _storm.ls.num\_files_ property in _test.properties_) under the directory _storm.ls.base\_file\_path_. For creating this files you can use the _fixture.sh_ script in the _bin_ directory.

Edit the properties file under _storm/ls_ providing the endpoint of the service to test and other information, and run either using the runAgent script in the bin directory or directly using

	java -cp /opt/grinder-3.11/lib/*:lib/* net.grinder.Grinder storm/ls/test.properties

(this suppose grinder is installed in /opt/grinder-3.11, change according to your installation).
