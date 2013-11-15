#!/bin/sh

#  uploader.sh
#  
#
#  Created by Enrico Vianello on 11/11/13.
#

#!/bin/sh

#  launcher.sh
#
#
#  Created by Enrico Vianello on 05/11/13.
#

TEST_ID=1

REMOTE_DIR="stress-test/atlasrenaming/input"

echo "************** UPLOADER ****************"
hostname=$1
echo "hostname: $hostname"
vo=$2
echo "vo: $vo"
nfiles=$3
echo "nfiles: $nfiles"

echo "create sourcefile"
dd if=/dev/urandom of=/tmp/sourcefile bs=1k count=1

options="--cert $X509_USER_PROXY --cacert $HOME/.globus/usercert.pem --capath /etc/grid-security/certificates"

echo "create remote input directories"
output=$(curl --head -I $options https://$hostname:8443/webdav/$vo/stress-test)
if [[ "$output" == *"200 OK"* ]]; then
	output=$(curl --head -I $options https://$hostname:8443/webdav/$vo/stress-test/atlasrenaming)
	if [[ "$output" == *"200 OK"* ]]; then
		echo "stress-test/atlasrenaming directory exists"
		output=$(curl --head -I $options https://$hostname:8443/webdav/$vo/stress-test/atlasrenaming/input)
		if [[ "$output" == *"200 OK"* ]]; then
			echo "stress-test/atlasrenaming/input directory exists"
		else
			output=$(curl -X MKCOL -I $options https://$hostname:8443/webdav/$vo/stress-test/atlasrenaming/input)
			echo "$output"
			output=$(curl -X MKCOL -I $options https://$hostname:8443/webdav/$vo/stress-test/atlasrenaming/output)
			echo "$output"
		fi
	else
		output=$(curl -X MKCOL -I $options https://$hostname:8443/webdav/$vo/stress-test/atlasrenaming)
		echo "$output"
		output=$(curl -X MKCOL -I $options https://$hostname:8443/webdav/$vo/stress-test/atlasrenaming/input)
		echo "$output"
		output=$(curl -X MKCOL -I $options https://$hostname:8443/webdav/$vo/stress-test/atlasrenaming/output)
		echo "$output"
	fi
else
	output=$(curl -X MKCOL -I $options https://$hostname:8443/webdav/$vo/stress-test)
	echo "$output"
	output=$(curl -X MKCOL -I $options https://$hostname:8443/webdav/$vo/stress-test/atlasrenaming)
	echo "$output"
	output=$(curl -X MKCOL -I $options https://$hostname:8443/webdav/$vo/stress-test/atlasrenaming/input)
	echo "$output"
	output=$(curl -X MKCOL -I $options https://$hostname:8443/webdav/$vo/stress-test/atlasrenaming/output)
	echo "$output"
fi

for ((i=0;i<$nfiles;i++)); do
    lcg-cp -b -D srmv2 file:///tmp/sourcefile srm://$hostname:8444/srm/managerv2?SFN=/$vo/stress-test/atlasrenaming/input/test_$i
    echo "/$vo/test_$TEST_ID/test_$i created"
done

exit 0