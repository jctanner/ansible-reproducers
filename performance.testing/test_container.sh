#!/bin/bash

CONTAINERS="ansible-el7:1.0 ansible-f27:1.0"
AVERSIONS="ansible==2.4.4.0 ansible==2.5.0 ansible==2.5.1 ansible==2.5.3 git+https://github.com/ansible/ansible"
FORKCOUNTS="5 25"
REMOTE_USERS="root testuser"
BECOME_VALS="False True"
PIPELINING_VALS="0 1"
INVENTORIES="inventory_generated.ini inventory_generated_keys.ini"

RESDIR="results"
if [[ ! -d $RESDIR ]]; then
    mkdir -p $RESDIR
#else
#    rm -rf $RESDIR
#    mkdir -p $RESDIR
fi

counter=0
for CONTAINER in $CONTAINERS; do
    for AVERSION in $AVERSIONS; do
        for FORKS in $FORKCOUNTS; do
            for REMOTE_USER in $REMOTE_USERS; do
                for BECOMEVAL in $BECOME_VALS; do
                    for PIPELINING_VAL in $PIPELINING_VALS; do
                        for INVENTORY in $INVENTORIES; do
                            echo "COUNT: $counter"

                            # don't repeat previous runs
                            if [[ -f $RESDIR/${counter}.docker.log ]]; then
                                echo "skippping re-running $counter"
                                let "counter++"
                                continue
                            fi

                            # don't use pipelining and sshpass together
                            if [[ $INVENTORY != *"key"* ]] && [[ $PIPELINING_VAL == "1" ]]; then
                                echo "skipping $INVENTORY + PIPELINING=$PIPELINING_VAL"
                                let "counter++"
                                continue
                            fi

                            # pipelining is generally problematic
                            if [[ $PIPELINING_VAL == "1" ]]; then
                                echo "skipping PIPELINING=$PIPELINING_VAL"
                                let "counter++"
                                continue
                            fi


                            EARGS=""
                            EARGS="$EARGS -e 'REMOTE_USER=${REMOTE_USER}'"
                            EARGS="$EARGS -e 'REMOTE_BECOME=${BECOMEVAL}'"

                            CMD="cd /root/playbooks;"
                            CMD="$CMD pip install ${AVERSION};"
                            CMD="$CMD ANSIBLE_PIPELINING=${PIPELINING_VAL}"
                            CMD="$CMD time ansible-playbook -vvvv $EARGS --forks=$FORKS -i $INVENTORY site.yml"
                            echo "${CMD}" > $RESDIR/${counter}.cmd

                            DCMD="docker run -v $(pwd):/root/playbooks $CONTAINER /bin/bash /root/playbooks/$RESDIR/${counter}.cmd"

                            echo "${DCMD}" > $RESDIR/${counter}.dcmd
                            echo "${DCMD}"
                            #$DCMD | tee -a $RESDIR/${counter}.log ; echo ${PIPESTATUS[0]} > $RESDIR/${counter}.rc
                            timeout -s SIGKILL 10m $DCMD
                            CID=$(docker ps -a | head -n2 | tail -n1 | awk '{print $1}')
                            docker logs $CID > $RESDIR/${counter}.docker.log 2>&1
                            docker kill $CID
                            docker rm $CID

                            #counter=$((counter+1)) 
                            let "counter++"
                            #exit 0
                        done
                    done
                done
            done
        done 
    done
done
