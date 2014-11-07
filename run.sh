#!/bin/bash

export GRINDER_PROCESSES=4
export GRINDER_THREADS=10
export GRINDER_USE_CONSOLE=true
export GRINDER_CONSOLE_HOST=dot1x-179.cnaf.infn.it
export GRINDER_RUNS=0

TEST="./storm/ptg-sync/test.properties"

echo "Test: $TEST"
echo "Processes: $GRINDER_PROCESSES"
echo "Threads: $GRINDER_THREADS"
echo "Runs: $GRINDER_RUNS"
echo "---"
echo "Removing logs"

rm -f log/*
./bin/runAgent.sh $TEST
