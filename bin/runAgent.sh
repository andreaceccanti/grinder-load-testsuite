#!/bin/bash
#set -x

LIBS=$(ls -1 lib/*.jar | tr '\n' ':')
GRINDERHOME="/opt/grinder-3.11"
CLASSPATH="lib:$LIBS$GRINDERHOME/lib/grinder.jar"
THIS_DIR="$( cd $( dirname ${BASH_SOURCE[0]}) && pwd )"
LOG_DIR="${THIS_DIR}/../log"
LOG_LEVEL="${GRINDER_LOG_LEVEL:-info}"
WORKER_LOG_LEVEL="${WORKER_LOG_LEVEL:-warn}"
PROCESSES="${GRINDER_PROCESSES:-1}"
THREADS="${GRINDER_THREADS:-2}"
JAVA_VM_OPTS=""
CONSOLE="${GRINDER_USE_CONSOLE:-false}"
CONSOLE_HOST="${GRINDER_CONSOLE_HOST:-localhost}"
RUNS="${GRINDER_RUNS:-1}"

JYTHONPATH="${THIS_DIR}/../storm/base" \
     java $JAVA_VM_OPTS \
        -Dgrinder.processes="${PROCESSES}" \
        -Dgrinder.threads="${THREADS}" \
        -Dgrinder.useConsole="${CONSOLE}" \
        -Dgrinder.consoleHost="${CONSOLE_HOST}" \
        -Dgrinder.runs="${RUNS}" \
        -Dgrinder.logLevel="${LOG_LEVEL}" \
        -Dworker.logLevel="${WORKER_LOG_LEVEL}" \
        -Dgrinder.logDirectory="${LOG_DIR}" \
        -classpath $CLASSPATH net.grinder.Grinder $1

