# 38892 reproducer

## purpose

Attempt to simulate ios_config at a moderate scale and reproduce https://github.com/ansible/ansible/issues/38892. 

This was used along with https://github.com/ansible/ansible/pull/39205 to find the fix in https://github.com/ansible/ansible/pull/39223

## instructions

1. Build the ios mock container

https://github.com/jctanner/ansible-tools/tree/master/docker/cisco-ios

2. Spawn the container many times

```
ansible-test-version devel build_network.sh
```

3. Run the test script

```
ansible-test-version devel test.sh
```

4. Parse the resulting log

```
python debugparser.py logs/ansible__v2.6.0_h100_f500.log
```

5. Read the parser output

```
$ python debugparser.py logs/ansible__v2.6.0_h100_f500.log
checksum: d8d8d7b921c7b8a436997576f4bb7b4b
med duration per fork: 10.0
med play offset per fork: 17.0
med task offset per fork: 6.0
max duration per fork: 14
max play offset per fork: 19
max task offset per fork: 8
time t0: 2018-04-24T01:03:11
time (e)t0: 2018-04-24T01:03:02
max task executor duration per host: 4
med task executor duration per host: 3.0
min task executor duration per host: 1
avg task executor duration per host: 3.2
172.17.0.8 [010] task executor duration: 1
172.17.0.8 [100] task executor duration: 3
172.17.0.9 [010] task executor duration: 1
172.17.0.9 [100] task executor duration: 3
172.17.0.3 [010] task executor duration: 1
172.17.0.3 [100] task executor duration: 3
172.17.0.6 [010] task executor duration: 1
172.17.0.6 [100] task executor duration: 3
172.17.0.7 [010] task executor duration: 1
172.17.0.7 [100] task executor duration: 3
172.17.0.4 [010] task executor duration: 1
172.17.0.4 [100] task executor duration: 3
172.17.0.5 [010] task executor duration: 1
172.17.0.5 [100] task executor duration: 3
172.17.0.10 [010] task executor duration: 1
172.17.0.10 [100] task executor duration: 3
172.17.0.11 [010] task executor duration: 1
172.17.0.11 [100] task executor duration: 3
172.17.0.12 [010] task executor duration: 1
172.17.0.12 [100] task executor duration: 3
```

If the issue has been "reproduced", the `max task executor duration per host` number will be much higher than the median.
