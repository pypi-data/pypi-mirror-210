#/bin/bash
export URL="https://idoit-test.int.yco.de/src/jsonrpc.php"
export IUSER="su-api"
export IPW=""
export API_KEY=""
curl -vv -H 'Content-Type: application/json' \
     -H "X-RPC-Auth-Username: $IUSER" \
     -H "X-RPC-Auth-Password: $IPW" \
     $URL --data-ascii @-  <<EOF 
{"id": 1, "jsonrpc": "2.0", "method": "cmdb.category.update", "params": {"apikey": "${API_KEY}", "category": "C__CATG__NETWORK_LOG_PORT", "data": {"active": 0, "addresses": null,"category_id": 3, "description": null, "mac": null, "net": null, "parent": null, "port_type": 2, 

 "ports": [
     "9046_C__CATG__NETWORK_PORT", 
     "9045_C__CATG__NETWORK_PORT"
     ],

"standard": null, "title": "bond0"},"objID": 3105}}
EOF



