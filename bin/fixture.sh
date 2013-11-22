#!/bin/bash
# prepare a StoRM service for load testing
# this script is supposed to be run on the service under test,
# in the testers.em-emi.eu directory

root_dir=stress-test

# files needed by ls srm load test
mkdir -p ${root_dir}/ls
for i in {1..1000}
do
  touch ${root_dir}/ls/f$i
  chown storm.storm ${root_dir}/ls/f$i
done

# files needed by srm rm load test

# will create directory d1, d2, ..
num_dir=10

# with files f1, f2, .. inside
num_files=1000

# create directories and files
mkdir -p ${root_dir}/rm
chown storm.storm ${root_dir}/rm
for (( i=1; i<=$num_dir; i++ ))
do
  mkdir -p ${root_dir}/rm/d$i
  chown storm.storm ${root_dir}/rm/d$i
  for (( j=1; j<=$num_files; j++ ))
  do
    touch ${root_dir}/rm/d$i/f$j
    chown storm.storm ${root_dir}/rm/d$i/f$j
  done
done

