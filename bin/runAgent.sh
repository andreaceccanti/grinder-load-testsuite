#!/bin/bash
. ./bin/setupEnv.sh
java -classpath $CLASSPATH net.grinder.Grinder $1
