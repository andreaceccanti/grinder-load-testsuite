#!/bin/sh

REMOTE_DIR="stress-test/Rmdir"

hostname=$1
echo "hostname: $hostname"
vo=$2
echo "vo: $vo"
ndirectories=$3
echo "ndirectories: $ndirectories"

options="--cert $X509_USER_PROXY --cacert $HOME/.globus/usercert.pem --capath /etc/grid-security/certificates"

echo "create remote input directories"
for ((i=0;i<$ndirectories;i++)); do
	output=$(curl -X MKCOL -i $options https://$hostname:8443/webdav/$vo/$REMOTE_DIR/dir_$i)
	echo $output
done

exit 0