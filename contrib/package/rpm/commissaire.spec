Name:           commissaire
Version:        0.0.1rc1
Release:        1%{?dist}
Summary:        Simple cluster host management
License:        AGPLv3+
URL:            http://github.com/projectatomic/commissaire
Source0:        https://github.com/projectatomic/%{name}/archive/%{version}.tar.gz

BuildArch:      noarch

BuildRequires:  python-devel

# For docs
BuildRequires:  python-sphinx

# For tests
BuildRequires:  python-coverage
BuildRequires:  python-mock
BuildRequires:  python-nose
BuildRequires:  python-pep8

# XXX: Waiting on python2-python-etcd to pass review
#      https://bugzilla.redhat.com/show_bug.cgi?id=1310796
Requires:  python-setuptools
Requires:  python2-falcon
Requires:  python2-python-etcd
Requires:  python-gevent
Requires:  python-jinja2
Requires:  python-requests
Requires:  py-bcrypt
Requires:  ansible

%description
Commissaire allows administrators of a Kubernetes, Atomic Enterprise or
OpenShift installation to perform administrative tasks without the need
to write custom scripts or manually intervene on systems.

Example tasks include:
  * rolling reboot of cluster hosts
  * upgrade software on cluster hosts
  * check the status of cluster hosts
  * scan for known vulnerabilities
  * add a new host to a cluster for container orchestration


%prep
%autosetup


%build
%py2_build

# Build docs
%{__python2} setup.py build_sphinx -c doc -b text


%install
%py2_install


%check
# XXX: Issue with the coverage module.
#%{__python2} setup.py nosetests


%files
%license COPYING
%doc README.md
%doc doc/apidoc/*.rst
%{_bindir}/commctl
%{_bindir}/commissaire
%{_bindir}/commissaire-hashpass
%{python2_sitelib}/*


%changelog
* Mon Feb 22 2016 Matthew Barnes <mbarnes@redhat.com> - 0.0.1rc1-1
- Initial packaging.
