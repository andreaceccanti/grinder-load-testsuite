#!/bin/bash

export TESTSUITE_REPO="${TESTSUITE_REPO:-git://github.com/italiangrid/grinder-load-testsuite.git}"
export TESTSUITE_BRANCH="${TESTSUITE_BRANCH:-develop}"

export PROXY_VONAME="${PROXY_VONAME:-test.vo}"
export PROXY_USER="${PROXY_USER:-test0}"

export GRINDER_PROCESSES="${GRINDER_PROCESSES:-4}"
export GRINDER_THREADS="${GRINDER_THREADS:-10}"
export GRINDER_RUNS="${GRINDER_RUNS:-10000}"
export GRINDER_CONSOLE_USE="${GRINDER_CONSOLE_USE:-false}"
export GRINDER_CONSOLE_HOST="${GRINDER_CONSOLE_HOST:-localhost}"
GRINDER_TEST="${GRINDER_TEST:-srm_all}"
export GRINDER_SCRIPT="./storm/$GRINDER_TEST/$GRINDER_TEST.py"

export COMMON_STORM_FE_ENDPOINT_LIST="${COMMON_STORM_FE_ENDPOINT_LIST:-storm-test.cr.cnaf.infn.it:8444}"
export COMMON_STORM_DAV_ENDPOINT_LIST="${COMMON_STORM_DAV_ENDPOINT_LIST:-storm-test.cr.cnaf.infn.it:8443}"
export COMMON_TEST_STORAGEAREA="${COMMON_TEST_STORAGEAREA:-test.vo}"

export LOGGING_LEVEL="${LOGGING_LEVEL:-INFO}"

export CERT_DIR="/usr/share/igi-test-ca"
export PROPFILE="/etc/storm/grinder/testsuite.properties"

export PROXYFILE="/assets/proxy"
PROPFILE="/tmp/testsuite.properties"

envsubst </assets/testsuite.properties.template >$PROPFILE

cat $PROPFILE

# proxy

if [ -f  $PROXYFILE ];
then
  echo "Proxy file found in $PROXYFILE ..."
  echo "Changing X509_USER_PROXY value to $PROXYFILE ..."
  export X509_USER_PROXY=$PROXYFILE
  echo "X509_USER_PROXY=$PROXYFILE"
  export ENABLE_CHECKPROXY=false
else

  echo "Create globus directory ..."
  rm -rf /home/tester/.globus
  mkdir -p /home/tester/.globus
  chown tester:tester -R /home/tester/.globus
  ls -latr /home/tester/.globus
  echo "Copy user certificate into globus directory ..."
  cp $CERT_DIR/${PROXY_USER}.cert.pem /home/tester/.globus/usercert.pem
  chmod 644 /home/tester/.globus/usercert.pem
  ls -latr /home/tester/.globus
  echo "Copy user key into globus directory ..."
  cp $CERT_DIR/${PROXY_USER}.key.pem /home/tester/.globus/userkey.pem
  chmod 400 /home/tester/.globus/userkey.pem
  ls -latr /home/tester/.globus

  echo "Create VOMS proxy for $proxy_vo VO and user $proxy_user ..."
  echo pass|voms-proxy-init -pwstdin --voms ${PROXY_VONAME}
  export ENABLE_CHECKPROXY=true
fi

# testsuite

echo "Clone grinder-load-testsuite repository ..."
git clone $TESTSUITE_REPO
cd /home/tester/grinder-load-testsuite
git checkout $TESTSUITE_BRANCH

cp $PROPFILE .

env | grep "GRINDER"

#write out current crontab
crontab -l > mycron
#echo new cron into cron file
echo "*/10 * * * * /assets/checkproxy.sh" >> mycron
#install new cron file
crontab mycron
rm mycron
#write out current crontab
crontab -l > mycron

sed -i "s/name=\"org.apache\" level=\"WARN\"/name=\"org.apache\" level=\"${LOGGING_LEVEL}\"/g" ./lib/logback.xml
sed -i "s/name=\"httpclient\" level=\"ERROR\"/name=\"httpclient\" level=\"${LOGGING_LEVEL}\"/g" ./lib/logback.xml
sed -i "s/name=\"org.italiangrid.axis\" level=\"WARN\"/name=\"org.italiangrid.axis\" level=\"${LOGGING_LEVEL}\"/g" ./lib/logback.xml

sed -i "s/level=\"INFO\"/level=\"${LOGGING_LEVEL}\"/g" ./lib/logback-worker.xml
sed -i "s/level=\"WARN\"/level=\"${LOGGING_LEVEL}\"/g" ./lib/logback-worker.xml

echo "Run load testsuite ..."
./bin/runAgent.sh testsuite.properties
