%define name    mysql
%define version 5.7.16
%define release 5

%define pkgname %{name}-boost-%{version}.tar.gz

%define m_uid   27
%define m_gid   27
%define m_user  mysql
%define m_group mysql

%define cnfile      /etc/my.cnf
%define prefix      /usr/local/mysql
%define datadir     /data/db/mysql
%define logdir      /data/log/mysql
%define socket      /dev/shm/mysql.sock
%define charset     utf8
%define collation   utf8_general_ci

%define boost       boost/boost_1_59_0/

%define configdir   %{_sourcedir}/config

Name:       %{name}
Version:    %{version}
Release:    1%{?dist}
Summary:    MySQL Server %{version}

License:    MySQL FOSS License Exception
URL:        http://www.mysql.com/about/legal/licensing/foss-exception.html
Source0:    %{pkgname}

Group:      Applications/Databases

%description
MySQL Server

%prep
cp -rfv %{_sourcedir}/%{pkgname} . && tar zxf %{pkgname}
cd %{name}-%{version}

cmake . -DCMAKE_INSTALL_PREFIX=%{prefix} -DMYSQL_UNIX_ADDR=%{socket} \
        -DDEFAULT_CHARSET=%{charset} -DDEFAULT_COLLATION=%{collation} \
        -DMYSQL_DATADIR=%{datadir} -DWITH_BOOST=%{boost}

%build
cd %{name}-%{version}
make


%install
cd %{name}-%{version}
make install INSTALL="install -p" DESTDIR=$RPM_BUILD_ROOT

cp -rfv %{configdir}/my.cnf ${RPM_BUILD_ROOT}%{prefix}

%files
%defattr (-,root,root)
/etc/my.cnf
%{prefix}

%doc

%changelog

%post
cp -rf %{prefix}/support-files/mysql.server /etc/init.d/mysql
chmod 750 /etc/init.d/mysql

groups %{m_group} > /dev/null 2>&1 || groupadd -g %{m_gid} %{m_group}
id     %{m_user}  > /dev/null 2>&1 || useradd  -g %{m_gid} -u %{m_uid} %{m_user} -M -s /sbin/nologin -d /var/lib/mysql

mkdir -p %{datadir}
mkdir -p %{logdir}

for i in %{prefix}/bin/*
do
    ln -sv $i /usr/local/bin/$(basename $i) 2> /dev/null
done

echo "ALTER USER 'root'@'localhost' IDENTIFIED BY '123456';" > %{prefix}/support-files/reset-root-password 

%postun
for i in `ls -l /usr/local/bin | grep '/mysql' | awk '{print $9}'`
do
    echo -e "Removing $i"
    test -h /usr/local/bin/$i && rm -f /usr/local/bin/$i
done
