Commissaire
===========
A REST based cluster manager.

[![Documentation](https://readthedocs.org/projects/commissaire/badge/?version=latest)](http://commissaire.readthedocs.org/) [![Build Status](https://travis-ci.org/projectatomic/commissaire.svg)](https://travis-ci.org/projectatomic/commissaire)


Development: Getting Up And Running
===================================
To test out the current development code you will need the following installed:

- Python2.7
- virtualenv
- etcd2 (running)

Set up virtualenv
-----------------
```
$ virtualenv /where/you/want/it/to/live
...
(virtualenv)$ . /where/you/want/it/to/live/bin/activate
(virtualenv)$ pip install -r requirements.txt
...
```

(Optional): Run Unittests
-------------------------
From the repo root...

```
(virtualenv)$ pip install -r test-requirements.txt
...
(virtualenv)$ nosetests -v --with-coverage --cover-package commissaire --cover-min-percentage 80 test/
```

Adding a Host Manually
----------------------
Verify that etcd is running then execute...


```
(virtualenv)$ etcdctl set /commissaire/hosts/10.0.0.1 '{"address": "10.0.0.1","status": "available","os": "atomic","cpus": 2,"memory": 11989228,"space": 487652,"last_check": "2015-12-17T15:48:18.710454"}'
```

Running the service
-------------------
From the repo root...

```
(virtualenv)$ PYTHONPATH=`pwd`/src python src/commissaire/script.py &
...
```


Implemented Endpoints
=====================


/api/v0/host/$IP
----------------

GET
~~~
```json
{
    "address": string,
    "cluster": string,
    "status": string,
    "os": string,
    "cpus": int,
    "memory": int,
    "space": int,
    "last_check": string
}
```
