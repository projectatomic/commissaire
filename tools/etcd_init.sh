#!/bin/bash
#
# Creates the expected etcd directories for Commissaire

set -euo pipefail

echo "+ Creating Commissaire keyspaces..."
for x in clusters cluster hosts networks status; do
  etcd_path="/commissaire/"$x
  echo "++ Creating $etcd_path"
  etcdctl mkdir $etcd_path || true
done

echo "+ Creating default network configuration..."
DEFAULT_NETWORK_JSON=`python -c "from commissaire.constants import DEFAULT_CLUSTER_NETWORK_JSON; print(str(DEFAULT_CLUSTER_NETWORK_JSON).replace('\'', '\"'))"`
etcdctl set /commissaire/networks/default "$DEFAULT_NETWORK_JSON"


echo "+ Commissaire etcd namesapce now looks like the following:"
etcdctl ls --recursive /commissaire/
