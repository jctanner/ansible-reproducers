#!/usr/bin/env python

import glob
import os


def main():

    observations = []

    # results/<number>.cmd
    # results/<number>.dcmd
    # results/<number>.docker.log
    cmd_files = glob.glob('results/*.cmd')

    for cmd_file in cmd_files:
        number = cmd_file.split('/')[-1].split('.')[0]
        #print(number)

        docker_cmd_file = 'results/%s.dcmd' % number
        docker_log_file = 'results/%s.docker.log' % number

        if not os.path.isfile(docker_cmd_file):
            continue

        if not os.path.isfile(docker_log_file):
            continue

        with open(cmd_file, 'r') as f:
            cmd = f.read()

        with open(docker_cmd_file, 'r') as f:
            docker_cmd = f.read()

        with open(docker_log_file, 'r') as f:
            docker_log = f.readlines()

        container = docker_cmd.split()[4].replace(';', '')

        if 'elapsed' in docker_log[-2]:
            duration = docker_log[-2].split()[2].replace('elapsed', '')
        elif 'SSH: EXEC' in docker_log[-1]:
            continue
        else:
            #import epdb; epdb.st()
            continue

        hostcount = 0
        for line in docker_log:
            if ': ok=' in line and 'changed=' in line and 'unreachable=' in line:
                hostcount += 1

        obs = {
            'cmd': cmd.strip(),
            'docker_cmd': docker_cmd.strip(),
            'container': container,
            'duration': duration,
            'version': None,
            'pipelining': None,
            'user': None,
            'become': None,
            'forks': None,
            'sshkeys': None,
            'sshpass': None,
            'hosts': hostcount
        }

        for cpart in cmd.split():
            #print(cpart)
            if cpart.startswith('ansible=='):
                obs['version'] = cpart.split('==')[-1].replace(';', '')
            elif cpart.startswith('git+'):
                obs['version'] = 'devel'
            elif cpart.startswith('ANSIBLE_PIPELINING'):
                obs['pipelining'] = int(cpart.split('=')[-1])
            elif 'REMOTE_USER' in cpart:
                obs['user'] = cpart.split('=')[-1].replace("'", '')
            elif 'REMOTE_BECOME' in cpart:
                obs['become'] = cpart.split('=')[-1].replace("'", '')
            elif cpart.startswith("--forks"):
                obs['forks'] = int(cpart.split('=')[-1].replace("'", ''))
            elif cpart.startswith("inventory_"):
                if 'keys' in cpart:
                    obs['sshkeys'] = True
                    obs['sshpass'] = False
                else:
                    obs['sshkeys'] = False
                    obs['sshpass'] = True

        observations.append(obs)

    cols = ['duration', 'version', 'container', 'hosts', 'forks' ,'sshkeys', 'sshpass', 'pipelining', 'become']
    print(','.join(cols))
    for obs in sorted(observations, key=lambda x: x['duration'], reverse=True):
        vals = []
        for col in cols:
            vals.append(str(obs[col]))
        print(','.join(vals))

    #import epdb; epdb.st()


if __name__ == "__main__":
    main()
