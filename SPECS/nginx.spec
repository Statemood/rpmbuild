%define pcre_ver    8.39
%define pcre_pkg    pcre-%{pcre_ver}.tar.gz
%define ssl_ver     1.0.2j
%define ssl_pkg     openssl-%{ssl_ver}.tar.gz

%define ngx_user    nobody
%define ngx_group   nobody

%define ngx_prefix  /usr/local/nginx
%define ngx_log     /data/log/nginx

%define ngx_tmp             /dev/shm/nginx
%define ngx_tmp_client_body %{ngx_tmp}/client-body
%define ngx_tmp_proxy       %{ngx_tmp}/proxy
%define ngx_tmp_fastcgi     %{ngx_tmp}/fastcgi
%define ngx_tmp_uwsgi       %{ngx_tmp}/uwsgi
%define ngx_tmp_scgi        %{ngx_tmp}/scgi

Name:       nginx
Version:    1.10.2
Release:    1%{?dist}
Summary:    Nginx

Group:      Applications/Internet
License:    BSD
URL:        http://nginx.org
Source0:    %{name}-%{version}.tar.gz

%description
Nginx with OpenSSL

%prep
for src in %{pcre_pkg} %{ssl_pkg} %{name}-%{version}.tar.gz
do
    cp -v %{_sourcedir}/$src . && tar zxf $src
done

%build
cd %{name}-%{version}
./configure \
    --user=%{ngx_user}  \
    --group=%{ngx_group} \
    --prefix=%{ngx_prefix}  \
    --lock-path=%{ngx_tmp} \
    --error-log-path=%{ngx_log}/error.log \
    --http-log-path=%{ngx_log}/access.log \
    --with-http_ssl_module \
    --with-http_gzip_static_module \
    --with-http_stub_status_module \
    --with-http_v2_module \
    --with-http_realip_module \
    --with-http_flv_module \
    --with-http_mp4_module \
    --with-http_secure_link_module \
    --with-file-aio \
    --with-threads  \
    --with-stream=dynamic \
    --with-stream_ssl_module \
    --with-pcre=../pcre-%{pcre_ver} \
    --with-openssl=../openssl-%{ssl_ver} \
    --http-client-body-temp-path=%{ngx_tmp_client_body} \
    --http-proxy-temp-path=%{ngx_tmp_proxy} \
    --http-fastcgi-temp-path=%{ngx_tmp_fastcgi} \
    --http-uwsgi-temp-path=%{ngx_tmp_uwsgi} \
    --http-scgi-temp-path=%{ngx_tmp_scgi}

make 

%install
cd %{name}-%{version}
make install DESTDIR=%{buildroot}

cp -rfv %{_sourcedir}/config/nginx.conf %{buildroot}/%{ngx_prefix}/conf

%post
for d in %{ngx_log} %{ngx_tmp} 
do
    test -d $d || mkdir -p $d
done

echo "# Create Nginx temp dir on /dev/shm/nginx"    >> /etc/rc.local
echo "test -d %{ngx_tmp} || mkdir %{ngx_tmp}"       >> /etc/rc.local 

%files
%doc
%{ngx_prefix}

%changelog
