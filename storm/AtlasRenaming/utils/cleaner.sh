#!/bin/sh

#  cleaner.sh
#  
#
#  Created by Enrico Vianello on 11/11/13.
#

TEST_ID=1

echo "************** CLEANER ****************"
hostname=$1
echo "hostname: $hostname"
vo=$2
echo "vo: $vo"

options="--cert $X509_USER_PROXY --cacert $HOME/.globus/usercert.pem --capath /etc/grid-security/certificates"

echo "delete remote input directory"
output=$(curl -X DELETE -I $options https://$hostname:8443/webdav/$vo/stress-test/atlasrenaming/output)

if [[ "$output" == *"204 No Content"* ]]; then
    echo "DELETE /webdav/$vo/test_$TEST_ID OK"
else
    echo "DELETE /webdav/$vo/test_$TEST_ID failed"
    exit 1
fi

exit 0