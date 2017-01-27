#!/bin/bash
#
# Start file for all-in-one
set -eo pipefail

# Start up required services
redis-server /etc/redis.conf &
etcd --data-dir=/data/etcd/ &

# Enter the virtual environment
. /environment/bin/activate
# Populat etcd
./etcd_init.sh

# Start up commissaire services
commissaire-storage-service &
commissaire-clusterexec-service &
commissaire-investigator-service &
commissaire-watcher-service &
commissaire-containermgr-service &
commissaire-server
