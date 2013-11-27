#!/bin/bash
#set -x

LIBS=$(ls -1 lib/*.jar | tr '\n' ':')
GRINDERHOME="/opt/grinder-3.11"
CLASSPATH="lib:$LIBS$GRINDERHOME/lib/grinder.jar"
THIS_DIR="$( cd $( dirname ${BASH_SOURCE[0]}) && pwd )"
LOG_DIR="${THIS_DIR}/../log"

JYTHONPATH="${THIS_DIR}/../storm/base" \
    java -Dgrinder.logDirectory="${LOG_DIR}" -classpath $CLASSPATH net.grinder.Grinder $1
