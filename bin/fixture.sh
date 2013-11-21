#!/bin/bash
# prepare a StoRM service for load testing
# this script is supposed to be run on the service under test,
# in the testers.em-emi.eu directory

root_dir=stress-test

# files needed by ls srm load test
mkdir -p ${root_dir}/ls
for i in {1..1000}
do
	touch stress-test/ls/f$i
done

