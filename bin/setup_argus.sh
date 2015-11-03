#!/bin/bash
set -e

pap-admin remove-all-policies

for idx in `seq 1 100`; do
	label=`printf '%03d' $idx`
	pap-admin add-policy --resource http://test.local.io/wn`echo $label` \
		--obligation "http://glite.org/xacml/obligation/local-environment-map" \
		--action ANY \
		permit subject="CN=test0,O=IGI,C=IT"
	
	let "n=idx+100"
	label=`printf '%03d' $n`
	pap-admin add-policy --resource http://test.local.io/wn`echo $label` \
		 --obligation "http://glite.org/xacml/obligation/local-environment-map" \
		 --action ANY \
		 deny subject="CN=test0,O=IGI,C=IT"
done

/etc/init.d/argus-pepd clearcache
/etc/init.d/argus-pdp reloadpolicy