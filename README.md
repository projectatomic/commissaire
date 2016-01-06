Commissaire
===========
A REST based cluster manager.

[![Build Status](https://travis-ci.org/projectatomic/commissaire.svg)](https://travis-ci.org/projectatomic/commissaire)


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
