#!/bin/bash
set -xe

policyfile=/tmp/policy.txt
pap-admin remove-all-policies

rm -vf $policyfile

set +x

for idx in `seq 1 1000`; do
	n_permit=`printf '%03d' $idx`
	let "n=idx+1000"
	n_deny=`printf '%03d' $n`
	
	cat <<EOF >> $policyfile
	
resource "http://test.local.io/wn`echo $n_permit`" {
	obligation "http://glite.org/xacml/obligation/local-environment-map" {}
    action "ANY" {
        rule permit { subject="CN=test0,O=IGI,C=IT" }
    }
}

resource "http://test.local.io/wn`echo $n_deny`" {
	obligation "http://glite.org/xacml/obligation/local-environment-map" {}
    action "ANY" {
        rule deny { subject="CN=test0,O=IGI,C=IT" }
    }
}
EOF

done

set -x

pap-admin add-policies-from-file $policyfile

/etc/init.d/argus-pepd clearcache
/etc/init.d/argus-pdp reloadpolicy