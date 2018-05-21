#!/bin/bash

ANSIBLE_CALLBACK_WHITELIST="profile_tasks" \
    PROFILE_TASKS_TASK_OUTPUT_LIMIT=100 \
    ansible-playbook -vvvv --forks=25 -i inventory_generated.ini site.yml
#time ansible-playbook -vvvv -i inventory_generated.ini site.yml
