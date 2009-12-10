#
# Copyright (c) 2009 SUSE LINUX Products GmbH, Nuernberg, Germany.
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes or comments via http://bugs.opensuse.org/
#

# norootforbuild

# 
# Since this spec file supports multiple distributions, ensure we
# use the correct group for each.
#

%define uid 90
%define gname haclient
%define uname hacluster

Name:           cluster-glue
Summary:        Reusable cluster components
Version:        1.0.2
Release:	0rc1%{?dist}
License:        GPL v2 or later; LGPL v2.1 or later
Url:            http://www.linux-ha.org
Group:		Productivity/Clustering/HA
Source:         cluster-glue.tar.bz2
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
AutoReqProv:    on
BuildRequires:  automake autoconf libtool e2fsprogs-devel glib2-devel pkgconfig python-devel libxml2-devel
BuildRequires:  libnet net-snmp-devel OpenIPMI-devel openhpi-devel 

Obsoletes:	heartbeat-common
Requires(pre):    /usr/sbin/groupadd /usr/bin/getent /usr/sbin/useradd

# SLES10 needs tcpd-devel but doesn't have libcurl
%if 0%{?suse_version} < 1020
BuildRequires:  tcpd-devel
%else
BuildRequires:  libcurl-devel 
%endif

%description
A collection of common tools derived from the Heartbeat project that are 
useful for writing cluster managers such as Pacemaker.
Provides a local resource manager that understands the OCF and LSB
standards, and an interface to common STONITH devices.

%package -n libglue2
License:        GPL v2 only; GPL v2 or later; LGPL v2.1 or later
Summary:        The Pacemaker scalable High-Availability cluster resource manager
Group:		Productivity/Clustering/HA
Obsoletes:	libheartbeat2
Requires:       %{name} = %{version}-%{release}

%description -n libglue2
A collection of libraries that are useful for writing cluster managers 
such as Pacemaker.

%package -n libglue-devel 
License:        GPL v2 only; GPL v2 or later; LGPL v2.1 or later
Summary:        The Pacemaker scalable High-Availability cluster resource manager
Group:		Development/Libraries/C and C++
Requires:       %{name} = %{version}-%{release}
Requires:       libglue2 = %{version}-%{release}
Obsoletes:	libheartbeat-devel

%description -n libglue-devel
Headers and shared libraries for a useful for writing cluster managers 
such as Pacemaker.

%prep
###########################################################
%setup -n cluster-glue -q
###########################################################

%build
CFLAGS="${CFLAGS} ${RPM_OPT_FLAGS}"
export CFLAGS

./autogen.sh
%if 0%{?suse_version} < 1020
%configure \
    --enable-fatal-warnings=yes \
    --with-daemon-group=%{gname} \
    --with-daemon-user=%{uname}
%else
%configure --enable-fatal-warnings=yes --with-daemon-group=%{gname} --with-daemon-user=%{uname} --docdir=%{_docdir}
%endif
make %{?_smp_mflags}
###########################################################

%install
###########################################################
make DESTDIR=$RPM_BUILD_ROOT install
# Dont package static libs or compiled python
find $RPM_BUILD_ROOT -name '*.a' -type f -print0 | xargs -0 rm -f
find $RPM_BUILD_ROOT -name '*.la' -type f -print0 | xargs -0 rm -f
find $RPM_BUILD_ROOT -name '*.pyc' -type f -print0 | xargs -0 rm -f
find $RPM_BUILD_ROOT -name '*.pyo' -type f -print0 | xargs -0 rm -f

test -d $RPM_BUILD_ROOT/sbin || mkdir $RPM_BUILD_ROOT/sbin
(
  cd $RPM_BUILD_ROOT/sbin
  ln -s /etc/init.d/logd rclogd
)

###########################################################

%clean
###########################################################
if
  [ -n "${RPM_BUILD_ROOT}" -a "${RPM_BUILD_ROOT}" != "/" ]
then
  rm -rf $RPM_BUILD_ROOT
fi
rm -rf $RPM_BUILD_DIR/cluster-glue
###########################################################

%pre
if
  getent group %{gname} >/dev/null
then
  : OK group haclient already present
else
  /usr/sbin/groupadd -o -r -g %{uid} %{gname} 2>/dev/null || :
fi
if
  getent passwd %{uname} >/dev/null
then
  : OK hacluster user already present
else
  /usr/sbin/useradd -r -g %{gname} -c "heartbeat processes" \
        -d %{_var}/lib/heartbeat/cores/%{uname} -o -u %{uid} \
        %{uname} 2>/dev/null || :
fi

%post -n libglue2
/sbin/ldconfig  
  
%postun -n libglue2
/sbin/ldconfig

%files
###########################################################
%defattr(-,root,root)

%dir %{_libdir}/heartbeat
%dir %{_var}/lib/heartbeat
%dir %{_var}/lib/heartbeat/cores
%dir %attr (0700, root, root)           %{_var}/lib/heartbeat/cores/root
%dir %attr (0700, nobody, nobody)       %{_var}/lib/heartbeat/cores/nobody
%dir %attr (0700, %{uname}, %{gname})   %{_var}/lib/heartbeat/cores/%{uname}

%dir %{_libdir}/heartbeat/plugins
%dir %{_libdir}/heartbeat/plugins/RAExec
%dir %{_libdir}/heartbeat/plugins/InterfaceMgr

%dir %{_libdir}/stonith
%dir %{_libdir}/stonith/plugins
%dir %{_libdir}/stonith/plugins/stonith2

%dir %{_datadir}/heartbeat
%{_datadir}/heartbeat/ha_cf_support.sh
%{_datadir}/heartbeat/openais_conf_support.sh
%{_datadir}/heartbeat/utillib.sh
%{_datadir}/heartbeat/combine-logs.pl

%{_sbindir}/ha_logger
%{_sbindir}/hb_report
%{_sbindir}/lrmadmin
%{_sbindir}/meatclient
%{_sbindir}/stonith
%{_sbindir}/sbd

%{_sysconfdir}/init.d/logd

%doc %{_mandir}/man1/*
%doc %{_mandir}/man8/*
%doc AUTHORS
%doc COPYING
%doc logd/logd.cf
%doc doc/stonith/README*

/sbin/rclogd

%{_libdir}/heartbeat/lrmd
%{_libdir}/heartbeat/ha_logd

%{_libdir}/heartbeat/plugins/RAExec/*.so
%{_libdir}/heartbeat/plugins/InterfaceMgr/*.so

%{_libdir}/stonith/plugins/external
%{_libdir}/stonith/plugins/stonith2/*.so
%{_libdir}/stonith/plugins/stonith2/*.py
%{_libdir}/stonith/plugins/xen0-ha-dom0-stonith-helper

%files -n libglue2
%defattr(-,root,root)
%{_libdir}/lib*.so.*
%doc AUTHORS
%doc COPYING.LIB

%files -n libglue-devel
%defattr(-,root,root)

%dir %{_libdir}/heartbeat
%dir %{_libdir}/heartbeat/plugins
%dir %{_libdir}/heartbeat/plugins/test
%dir %{_datadir}/heartbeat

%{_libdir}/lib*.so
%{_libdir}/heartbeat/ipctest
%{_libdir}/heartbeat/ipctransientclient
%{_libdir}/heartbeat/ipctransientserver
%{_libdir}/heartbeat/transient-test.sh
%{_libdir}/heartbeat/base64_md5_test
%{_libdir}/heartbeat/logtest
%{_includedir}/clplumbing
%{_includedir}/heartbeat
%{_includedir}/stonith
%{_includedir}/pils
%{_datadir}/heartbeat/lrmtest
%{_libdir}/heartbeat/plugins/test/test.so
%doc AUTHORS
%doc COPYING
%doc COPYING.LIB

%changelog