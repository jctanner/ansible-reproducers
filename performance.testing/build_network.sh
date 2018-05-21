#!/bin/bash

# https://github.com/moby/moby/issues/1044
#   This will cause network+dbus failures on >35 containers.
sudo sysctl -w fs.inotify.max_user_instances=8192

export SSH_AUTH_SOCK=0
VERSION=$(ansible --version | head -n1 | awk '{print $2}')

TOTAL_NODES=198
#TOTAL_NODES=10
ansible-playbook -v -i inventory -e "total_nodes=$TOTAL_NODES" build_network.yml
RC=$?
echo "RC: $RC"
if [[ $RC != 0 ]]; then
    exit $RC
fi

if [ ! -f inventory_generated.ini ]; then
    echo "inventory_generated.ini file was not created"
    exit 1
fi

for NODE in $(egrep ^172 inventory_generated.ini | awk '{print $1}'); do
    ssh-keygen -R $NODE
done

for HASH in $(egrep ^172 inventory_generated.ini | awk '{print $4}' | cut -d\= -f2); do
    echo $HASH
    docker exec -it $HASH rm /var/run/nologin
done
