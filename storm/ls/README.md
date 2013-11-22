# Load test for SRM ls

Edit the properties file under storm/ls provinding the endpoint of the service to test and other information and run either using the runAgent script in the bin directory or directly using

	java -cp /opt/grinder-3.11/lib/*:lib/* net.grinder.Grinder storm/ls/test.properties

(this suppose grinder is installed in /opt/grinder-3.11, change according to your installation).