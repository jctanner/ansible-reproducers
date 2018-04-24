#!/usr/bin/env python

import datetime
import json
import os
import subprocess
import sys

import numpy as np
from pprint import pprint

def sha4file(filename):
    # MD5 (/Users/jtanner/Downloads/debug-check-10.log) = b3768266d9cbf8beaa5a415b0172ee01

    if os.path.exists('/usr/bin/md5sum'):
        cmd = 'md5sum %s' % filename
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
        (so, se) = p.communicate()
        so = so.strip()
        checksum = so.split()[0]
    elif os.path.exists('/sbin/md5'):
        cmd = 'md5 %s' % filename
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
        (so, se) = p.communicate()
        so = so.strip()
        checksum = so.split()[-1]

    return checksum


def line2time(line):
    ts = '_'.join(line.split()[0:2])
    ts = ts.split(',')[0]
    try:
        ts = datetime.datetime.strptime(ts, '%Y-%m-%d_%H:%M:%S')
    except Exception as e:
        return None
    return ts


def main():
    #logfile = '~/Downloads/debug-check-100.log'
    logfile = sys.argv[1]
    logfile = os.path.expanduser(logfile)

    if '_h' not in logfile:
        hostcount = logfile.split('-')[-1].replace('.log', '')
        hostcount = int(hostcount)
    else:
        fn = os.path.basename(logfile)
        parts = fn.split('_')
        parts = [x for x in parts if x.startswith('h')]
        hostcount = int(parts[0].replace('h', ''))

    checksum = sha4file(logfile)
    print('checksum: %s' % checksum)

    pids = {}
    hosts = {}

    parent = None
    p0 = None
    pN = None
    t0 = None
    et0 = None

    # 2018-04-19 21:35:52,856 p=23442 u=root |  PLAY [Run adhoc commands]
    # 2018-04-19 21:33:17,115 p=20287 u=root |   20855 1524173597.11550: firing event: on_close_shell()
    # 2018-04-19 21:28:12,295 p=19602 u=root |   19838 1524173292.28263: running TaskExecutor() for adkkglkancts01/TASK: Backup current config

    lc = 0
    with open(logfile, 'r') as f:
        for line in f.readlines():
            lc += 1

            if ' p=' in line:
                #print(lc)

                line = line.strip()

                pid = line.split()[2].split('=')[-1]
                if not pid.isdigit():
                    continue
                if not parent:
                    parent = pid

                ts = '_'.join(line.split()[0:2])
                ts = ts.split(',')[0]

                if 'PLAY [Run adhoc commands]' in line and not p0:
                    p0 = ts

                if 'TASK [Backup current config]' in line and not t0:
                    t0 = ts

                if 'PLAY RECAP' in line and not pN:
                    pN = ts

                if 'running TaskExecutor() for' in line and not 'done' in line:
                    hn = line.split()[10].split('/')[0]
                    if hn not in hosts:
                        hosts[hn] = {
                            'lines': [],
                            'timestamps': []
                        }
                        #hosts[hn]['lines'].append(line)
                    #print('total hosts: %s' % len(hosts.keys()))
                    if hn == 'for':
                        import epdb; epdb.st()

                '''
                if hosts:
                    chn = hosts.keys()[0]
                    if chn in line:
                        if line in hosts[chn]['lines']:
                            continue
                        hosts[chn]['lines'].append(line)
                '''

                if pid not in pids:
                    before_count = len(pids.keys())
                    pids[pid] = {
                        'pid': int(pid),
                        'timestamps': [],
                        'host': None,
                        'priors': before_count
                    }

                pids[pid]['timestamps'].append(ts)


    # reprocess for each host for data in the parent pid
    for k in hosts.keys():

        grep_dir = '/tmp/log_greps/%s' % checksum
        if not os.path.isdir(grep_dir):
            os.makedirs(grep_dir)

        grep_file = os.path.join(grep_dir, '%s.grep' % k)
        if not os.path.isfile(grep_file):
            cmd = "egrep '(\ %s$|\ %s\ | \[%s\]|\ %s\/)' %s > %s" % (k, k, k, k, logfile, grep_file)
            print(cmd)
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
            (so, se) = p.communicate()

        with open(grep_file, 'r') as f:
            lines = f.readlines()

        #lines = [x.strip() for x in lines if x.strip()]
        #lines = lines[:-1]

        ht0 = '_'.join(lines[0].split()[0:2])
        ht0 = ht0.split(',')[0]
        ht0 = datetime.datetime.strptime(ht0, '%Y-%m-%d_%H:%M:%S')

        htN = '_'.join(lines[-1].split()[0:2])
        htN = htN.split(',')[0]
        htN = datetime.datetime.strptime(htN, '%Y-%m-%d_%H:%M:%S')

        hosts[k]['start'] = ht0.isoformat()
        hosts[k]['stop'] = htN.isoformat()
        hosts[k]['duration'] = (htN - ht0).seconds

        estats = {
            'taskexecutor_start': None,
            'taskexecutor_stop': None,
            't0': line2time(lines[0]),
            'tN': line2time(lines[-1])
        }

        for line in lines:
            if 'Added host' in line:
                continue
            if 'Calling ' in line and 'to load vars' in line:
                continue
            if ' set ' in line and ' for %s' % k in line:
                continue
            if 'getting the next task for host' in line:
                continue
            if 'done getting next task for host' in line:
                continue
            if 'done getting next task for host' in line:
                continue
            if 'next free host:' in line:
                continue

            ts = '_'.join(line.split()[0:2])
            ts = ts.split(',')[0]
            try:
                ts = datetime.datetime.strptime(ts, '%Y-%m-%d_%H:%M:%S')
            except Exception as e:
                continue

            if ': running TaskExecutor()' in line:
                estats['taskexecutor_start'] = ts
            if ': done running TaskExecutor()' in line:
                estats['taskexecutor_stop'] = ts


            '''
            if '%s is blocked' % k in line:
                if not estats['blocked_start']:
                    estats['blocked_start'] = ts
                    continue

            if 'entering _queue_task()' in line:
                if not estats['entering _queue_task()']:
                    estats['entering _queue_task()'] = ts
                    continue
            if 'exiting _queue_task()' in line:
                if not estats['exiting _queue_task()']:
                    estats['exiting _queue_task()'] = ts
                    continue
            if 'running TaskExecutor() for' in line:
                if not estats['running TaskExecutor()']:
                    estats['running TaskExecutor()'] = ts
                    continue
                else:
                    import epdb; epdb.st()
            if 'done with _execute_module' in line:
                if not estats['done with _execute_module']:
                    estats['done with _execute_module'] = ts
                    continue
                else:
                    import epdb; epdb.st()
            '''

            #print(line)
            #import epdb; epdb.st()

        estats['te_duration'] = (estats['taskexecutor_stop'] - estats['taskexecutor_start']).seconds
        estats['te_offset'] = (estats['taskexecutor_start'] - estats['t0']).seconds
        estats['te_offset2'] = (estats['tN'] - estats['taskexecutor_stop']).seconds
        for k2,v2 in estats.items():
            hosts[k][k2] = v2
        #import epdb; epdb.st()

    # don't let the parent skew the stats
    ppid = pids.get(parent).copy()
    pids.pop(parent, None)

    # find duration and offset of each fork
    p0 = datetime.datetime.strptime(p0, '%Y-%m-%d_%H:%M:%S')
    t0 = datetime.datetime.strptime(t0, '%Y-%m-%d_%H:%M:%S')
    for k,v in pids.items():
        start = v['timestamps'][0]
        start = datetime.datetime.strptime(start, '%Y-%m-%d_%H:%M:%S')
        stop = v['timestamps'][-1]
        stop = datetime.datetime.strptime(stop, '%Y-%m-%d_%H:%M:%S')
        delta = (stop - start).seconds
        pids[k]['duration'] = delta
        pids[k]['p_offset'] = (stop - p0).seconds
        pids[k]['t_offset'] = (stop - t0).seconds

        if not et0:
            et0 = start
        elif start < et0:
            et0 = start

    # summarize data
    durations = sorted([x[1]['duration'] for x in pids.items()])
    t_offsets = sorted([x[1]['t_offset'] for x in pids.items()])
    p_offsets = sorted([x[1]['p_offset'] for x in pids.items()])

    print('med duration per fork: %s' % np.median(durations))
    print('med play offset per fork: %s' % np.median(p_offsets))
    print('med task offset per fork: %s' % np.median(t_offsets))

    print('max duration per fork: %s' % max(durations))
    print('max play offset per fork: %s' % max(p_offsets))
    print('max task offset per fork: %s' % max(t_offsets))

    print('time t0: %s' % (t0.isoformat()))
    print('time (e)t0: %s' % (et0.isoformat()))

    #with open('/tmp/%s.json' % chn, 'w') as f:
    #    data = hosts['

    te_durations = sorted([x[1]['te_duration'] for x in hosts.items()])
    print('max task executor duration per host: %s' % max(te_durations))
    print('med task executor duration per host: %s' % np.median(te_durations))
    print('min task executor duration per host: %s' % min(te_durations))
    print('avg task executor duration per host: %s' % np.mean(te_durations))

    for k,v in hosts.items():
        for k2, v2 in v.items():
            if isinstance(v2, datetime.datetime):
                hosts[k][k2] = v2.isoformat()

    jfile = '/tmp/10hosts.json'
    if hostcount == 10:
        jfile = '/tmp/10hosts.json'
        with open(jfile, 'w') as f:
            f.write(json.dumps(hosts, indent=2, sort_keys=True))

    if hostcount == 100:
        with open(jfile, 'r') as f:
            jdata = json.loads(f.read())
        for hn,hd in jdata.items():
            if hn in hosts:
                '''
                print('############################################')
                print('########### %s [10]' % hn)
                pprint(hd)
                print('########### %s [100]' % hn)
                pprint(hosts[hn])
                #import epdb; epdb.st()
                '''

                print('%s [010] task executor duration: %s' % (hn, hd['te_duration']))
                print('%s [100] task executor duration: %s' % (hn,hosts[hn]['te_duration']))

    max_ = max(te_durations)
    for k,v in hosts.items():
        if v['te_duration'] == max_:
            print('# %s' % k)
            pprint(v)
    import epdb; epdb.st()


if __name__ == "__main__":
    main()
