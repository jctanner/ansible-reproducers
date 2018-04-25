#!/bin/bash

rm -rf /tmp/fds
mkdir -p /tmp/fds

while true; do
    date
    THISDATE=$(date '+%Y-%m-%d_%H:%M:%S.%N')
    #for pid in $(pgrep ansible); do ls /proc/$pid/fd | wc -l; done;
    for PROC in $(ps aux | fgrep -i ansible | fgrep -v grep | awk '{print $2}'); do
        echo "PID: $PROC"
        CMD="$(cat /proc/$PROC/cmdline | tr '\0' ' ')"
        echo "$CMD" >  /tmp/fds/${PROC}_${THISDATE}.cmdline.txt
        #echo -e "\t$CMD"
        ls -al /proc/$PROC/fd > /tmp/fds/${PROC}_${THISDATE}.fds.txt
        #echo -e "\tPIPES: $(fgrep 'pipe:' /tmp/fds/$PROC.fds.txt | wc -l)"
        #echo -e "\tSOCKETS: $(fgrep 'socket:' /tmp/fds/$PROC.fds.txt | wc -l)"

        for PIP in $(fgrep 'pipe:' /tmp/fds/${PROC}_${THISDATE}.fds.txt | cut -d\[ -f2 | tr -d ']'); do
            echo $PIP
            lsof -n -P 2>/dev/null | fgrep $PIP  | fgrep -v "grep" > /tmp/fds/${PROC}_${THISDATE}.pipe.$PIP.txt
         done

    done
    sleep 0.1
done
