%define	major	2
%define	libname	%mklibname %{name} %{major}
%define	devname	%mklibname %{name} -d

# (tpg) this is important
# keep this synchronized with module-init-tools-ver-rel+1
%define module_ver 3.17-1

%bcond_without	dietlibc
%bcond_without	uclibc

Name:		kmod
Summary:	Utilities to load modules into the kernel
Version:	12
Release:	3
License:	LGPLv2.1+ and GPLv2+
Group:		System/Kernel and hardware
Url:		http://www.politreco.com/2011/12/announce-kmod-2/
# See also: http://packages.profusion.mobi/kmod/
Source0:	http://ftp.kernel.org/pub/linux/utils/kernel/kmod/%{name}-%{version}.tar.xz
Source1:	http://ftp.kernel.org/pub/linux/utils/kernel/kmod/%{name}-%{version}.tar.sign

# (tpg) provide config files from module-init-tools
Source2:	modprobe.default
Source3:	modprobe.preload
Source4:	blacklist-mdv.conf
Source5:	ipw-no-associate.conf
Source6:	blacklist-compat.conf

%if %{with dietlibc}
BuildRequires:	dietlibc-devel
%endif
%if %{with uclibc}
BuildRequires:	uClibc-devel >= 0.9.33.2-15
%endif
BuildRequires:	pkgconfig(liblzma)
BuildRequires:	pkgconfig(zlib)
BuildRequires:	xsltproc
BuildRequires:	gtk-doc


%description
kmod is a set of tools to handle common tasks with Linux kernel
modules like insert, remove, list, check properties, resolve
dependencies and aliases.

These tools are designed on top of libkmod, a library that is shipped
with kmod. The aim is to be compatible with tools, configurations and
indexes from module-init-tools project.

%package	compat
Summary:	Compat symlinks for kernel module utilities
License:	GPLv2+
Group:		System/Kernel and hardware
Obsoletes:	module-init-tools < %{module_ver}
Provides:	module-init-tools = %{module_ver}
Requires:	%{name} = %{EVRD}

%description	compat
kmod is a set of tools to handle common tasks with Linux kernel
modules like insert, remove, list, check properties, resolve
dependencies and aliases.

This package contains traditional name symlinks (lsmod, etc.)

%package -n	%{libname}
Summary:	Library to interact with Linux kernel modules
License:	LGPLv2.1+
Group:		System/Libraries
# (tpg) do not require this until initscripts won't be fixed
#Requires:	%{name}-compat = %{EVRD}
Conflicts:	%{mklibname modprobe 0} <= 3.6-18
Conflicts:	%{mklibname modprobe 1} < %{module_ver}

%description -n	%{libname}
libkmod was created to allow programs to easily insert, remove and
list modules, also checking its properties, dependencies and aliases.

%if %{with uclibc}
%package -n	uclibc-%{libname}
Summary:	Library to interact with Linux kernel modules
License:	LGPLv2.1+
Group:		System/Libraries

%description -n	uclibc-%{libname}
libkmod was created to allow programs to easily insert, remove and
list modules, also checking its properties, dependencies and aliases.
%endif

%package -n	%{devname}
Summary:	Development files for libkmod
Group:		Development/C
License:	LGPLv2.1+
Requires:	%{libname} = %{EVRD}
%if %{with uclibc}
Requires:	uclibc-%{libname} = %{EVRD}
%endif
Provides:	kmod-devel = %{EVRD}

%description -n	%{devname}
libkmod was created to allow programs to easily insert, remove and
list modules, also checking its properties, dependencies and aliases.

%prep
%setup -q

%build
export CONFIGURE_TOP=..
%if %{with dietlibc}
mkdir -p diet
pushd diet
CFLAGS="%{optflags} -fno-stack-protector -Os -D_BSD_SOURCE -D_FILE_OFFSET_BITS=64 -D_GNU_SOURCE -D_ATFILE_SOURCE -DO_CLOEXEC=0" \
%configure2_5x	--prefix=%{_prefix}/lib/dietlibc \
		--without-xz \
		--without-zlib \
		--with-rootlibdir=%{_prefix}/lib/dietlibc/lib-%{_arch} \
		--enable-static \
		--disable-shared \
		--disable-tools \
		CC="diet gcc" \
		LD="diet ld"
%make
popd
%endif

%if %{with uclibc}
mkdir -p uclibc
pushd uclibc
%uclibc_configure \
		--with-xz \
		--with-zlib \
		--with-rootlibdir=%{uclibc_root}/%{_lib} \
		--enable-static \
		--enable-shared \
		--disable-tools
%make V=1
popd
%endif

mkdir -p glibc
pushd glibc
# The extra --includedir gives us the possibility to detect dependent
# packages which fail to properly use pkgconfig.
%configure2_5x	--with-xz \
		--with-zlib \
		--includedir=%{_includedir}/%{name}-%{version} \
		--with-rootlibdir=/%{_lib} \
		--bindir=/bin \
		--enable-shared \
		--enable-static \
		--enable-gtk-doc \
		--enable-gtk-doc-html \
		--with-html-dir=%{_docdir}/%{name}/html
%make
popd

%install
%if %{with uclibc}
%makeinstall_std -C uclibc
rm %{buildroot}%{uclibc_root}%{_libdir}/libkmod.so
ln -rs %{buildroot}%{uclibc_root}/%{_lib}/libkmod.so.%{major}.* %{buildroot}%{uclibc_root}%{_libdir}/libkmod.so
rm -r %{buildroot}%{uclibc_root}%{_libdir}/pkgconfig/
%endif

%if %{with dietlibc}
install -m644 ./diet/libkmod/.libs/libkmod.a -D %{buildroot}%{_prefix}/lib/dietlibc/lib-%{_arch}/libkmod.a
#%makeinstall_std -C diet
%endif

%makeinstall_std -C glibc
# Remove standalone tools
rm -f %{buildroot}/bin/kmod-*
rm -f %{buildroot}%{_libdir}/libkmod.la

# (tpg) install config files
install -d -m755 %{buildroot}%{_sysconfdir}
install -d -m755 %{buildroot}%{_sysconfdir}/depmod.d
install -d -m755 %{buildroot}%{_sysconfdir}/modprobe.d
install -d -m755 %{buildroot}/lib/modprobe.d
install -m 644 %{SOURCE2} %{buildroot}%{_sysconfdir}/modprobe.d/00_modprobe.conf
install -m 644 %{SOURCE3} %{buildroot}%{_sysconfdir}
install -m 644 %{SOURCE4} %{SOURCE5} %{SOURCE6} %{buildroot}%{_sysconfdir}/modprobe.d
touch %{buildroot}%{_sysconfdir}/modprobe.conf

# (tpg) we still use this
ln -s ../modprobe.conf %{buildroot}%{_sysconfdir}/modprobe.d/01_mandriva.conf

# kmod-compat
mkdir -p %{buildroot}/{bin,sbin}
ln -s kmod %{buildroot}/bin/lsmod
for i in depmod insmod lsmod modinfo modprobe rmmod; do
	ln -s /bin/kmod %{buildroot}/sbin/$i
done;

%check
# make check suddenly seems to fail copy this directory from srcdir...
[ ! -d glibc/testsuite ] && cp -a testsuite glibc
make -C glibc check


%files
/bin/kmod
%{_mandir}/man5/*
%{_mandir}/man8/*

%files -n %{libname}
/%{_lib}/libkmod.so.%{major}*

%if %{with uclibc}
%files -n uclibc-%{libname}
%{uclibc_root}/%{_lib}/libkmod.so.%{major}*
%endif

%files -n %{devname}
%doc %{_docdir}/%{name}
%{_includedir}/*
%{_libdir}/pkgconfig/*.pc
%{_libdir}/libkmod.so
%{_libdir}/libkmod.a
%if %{with dietlibc}
%{_prefix}/lib/dietlibc/lib-%{_arch}/libkmod.a
%endif
%if %{with uclibc}
%{uclibc_root}%{_libdir}/libkmod.a
%{uclibc_root}%{_libdir}/libkmod.so
%endif

%files compat
%dir %{_sysconfdir}/modprobe.d
%dir %{_sysconfdir}/depmod.d
%dir /lib/modprobe.d
%config(noreplace) %{_sysconfdir}/modprobe.preload
%config(noreplace) %{_sysconfdir}/modprobe.conf
%config(noreplace) %{_sysconfdir}/modprobe.d/*.conf
/bin/lsmod
/sbin/*
