#!/bin/bash

export GRINDER_PROCESSES=1
export GRINDER_THREADS=1
export GRINDER_USE_CONSOLE=false
export GRINDER_CONSOLE_HOST=localhost
export GRINDER_RUNS=1

TEST="./storm/ptg-sync/test.properties"

echo "Test: $TEST"
echo "Processes: $GRINDER_PROCESSES"
echo "Threads: $GRINDER_THREADS"
echo "Runs: $GRINDER_RUNS"
echo "---"
echo "Removing logs"

rm -f log/*
./bin/runAgent.sh $TEST
