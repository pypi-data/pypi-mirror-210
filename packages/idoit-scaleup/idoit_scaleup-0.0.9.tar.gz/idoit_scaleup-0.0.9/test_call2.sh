#/bin/bash
export URL="https://idoit-test.int.yco.de/src/jsonrpc.php"
export IUSER="su-api"
export IPW="ugANE7vRNUECHhuK"
export API_KEY="c{88}4{RK,q_P/3m"
curl -H 'Content-Type: application/json' \
     -H "X-RPC-Auth-Username: $IUSER" \
     -H "X-RPC-Auth-Password: $IPW" \
     $URL --data-ascii @-  <<EOF 
{"id": 1, "jsonrpc": "2.0", "method": "cmdb.dialog.read", "params": {"apikey": "${API_KEY}", "category": "C__CATG__NETWORK_LOG_PORT", "property": "parent"}}
EOF



