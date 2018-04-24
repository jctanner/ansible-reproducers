#!/bin/bash
export SSH_AUTH_SOCK=0
VERSION=$(ansible --version | head -n1 | awk '{print $2}')

ps aux | fgrep -i ansible-connection | fgrep -v vim | awk '{print $2}' | xargs kill -9

rm -rf backup
rm -rf ~/.ansible/pc

HOSTSCOUNT=$(fgrep container_name inventory_generated.ini | wc -l)
FORKS=500
SLICE=100
#SLICE=10
#SLICE=2
#SLICE=1

date > /tmp/time_v${VERSION}_h${HOSTS}_f${FORKS}.start

rm -f ansible.log
rm -f /tmp/test_.log

#hosts_pattern="survey_hosts='cisco-ios[1:100]'"
hosts_pattern="survey_hosts='cisco-ios[1:$SLICE]'"
#hosts_pattern="survey_hosts='cisco-ios[1:1]'"

ANSIBLE_PARAMIKO_HOST_KEY_AUTO_ADD=True \
    ANSIBLE_DEBUG=1 \
    ansible-playbook -vvvv \
    -i inventory_generated.ini \
    --forks=$FORKS \
    -e "${hosts_pattern}" \
    site.yml

date > /tmp/time_v${VERSION}_h${HOSTS}_f${FORKS}.stop

RESDIR=logs
if [[ ! -d $RESDIR ]]; then
    mkdir -p $RESDIR
fi
cp ansible.log $RESDIR/ansible__v${VERSION}_h${SLICE}_f${FORKS}.log
#cp /tmp/test_.log $RESDIR/ansible_test_v${SLICE}_h${HOSTS}_f${FORKS}.log


echo $VERSION

RC=$?
exit $RC
