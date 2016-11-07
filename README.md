Commissaire
===========
The lightweight REST API for Node Management.

[![Documentation](https://readthedocs.org/projects/commissaire/badge/?version=latest)](http://commissaire.readthedocs.org/) [![Build Status](https://travis-ci.org/projectatomic/commissaire.svg)](https://travis-ci.org/projectatomic/commissaire)

**Note**: This repo now contains the common code used by Commissaire components. If you have an older checkout you will need to re-clone. For the original repo see [commissaire-mvp](https://www.github.com/projectatomic/commissaire-mvp/)


Related projects are:

**Official**:

  * [commissaire-service](https://github.com/projectatomic/commissaire-service) which provides the microservices and base code for the services.
  * [commissaire-http](https://github.com/projectatomic/commissaire-http) provides the HTTP REST front-end. It is responsible for routing of requests, the business logic, passing work to the services, and responding results back to the client.

**Community Projects**:

  * [commissaire-openstack](https://github.com/portdirect/commissaire-openstack)


Community Meeting
=================
See the [Community Meetings page](http://commissaire.readthedocs.io/en/latest/community_meetings.html).


Python Version
==============
Commissaire is intended to work on [Python 3.5+](https://docs.python.org/3.5/).

Building Docs
=============
Make sure you have  [Sphinx](http://www.sphinx-doc.org/en/stable/), [sphinx-rtd-theme](https://pypi.python.org/pypi/sphinx_rtd_theme), and [Setuptools](https://setuptools.readthedocs.io/en/latest/) installed.

```shell
$ python3 setup.py build_sphinx          # build to html
$ xdg-open build/sphinx/html/index.html  # open it up
```
