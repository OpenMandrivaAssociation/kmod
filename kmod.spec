%define	major	2
%define	libname	%mklibname %{name} %{major}
%define	devname	%mklibname %{name} -d

%bcond_without	dietlibc
%bcond_without	uclibc

Name:		kmod
Summary:	Utilities to load modules into the kernel
Version:	8
Release:	3
License:	LGPLv2.1+ and GPLv2+
Group:		System/Kernel and hardware
Url:		http://www.politreco.com/2011/12/announce-kmod-2/
# See also: http://packages.profusion.mobi/kmod/
Source0:	http://ftp.kernel.org/pub/linux/utils/kernel/kmod/%{name}-%{version}.tar.xz
Source1:	http://ftp.kernel.org/pub/linux/utils/kernel/kmod/%{name}-%{version}.tar.sign
%if %{with dietlibc}
BuildRequires:	dietlibc-devel
%endif
%if %{with uclibc}
BuildRequires:	uClibc-devel >= 0.9.33.2-3
%endif
BuildRequires:	pkgconfig >= 0.23 pkgconfig(liblzma) pkgconfig(zlib) xz

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
Conflicts:	module-init-tools
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

%description -n	%{libname}
libkmod was created to allow programs to easily insert, remove and
list modules, also checking its properties, dependencies and aliases.

%package -n	%{devname}
Summary:	Development files for libkmod
Group:		Development/C
License:	LGPLv2.1+
Requires:	%{libname} = %{EVRD}

%description -n	%{devname}
libkmod was created to allow programs to easily insert, remove and
list modules, also checking its properties, dependencies and aliases.

%prep
%setup -q

%build
%if %{with dietlibc}
mkdir diet
pushd diet
CC="diet gcc" ../configure --with-zlib --with-xz --enable-static --disable-shared --disable-tools
%make V=1 LD="diet ld" CC="diet cc" CFLAGS="-Os -D_BSD_SOURCE -D_FILE_OFFSET_BITS=64 -D_GNU_SOURCE -D_ATFILE_SOURCE -DO_CLOEXEC=0 -g -DUINT16_MAX=65535 -DINT32_MAX=2147483647"
popd
%endif

%if %{with uclibc}
mkdir uclibc
pushd uclibc
CC="%{uclibc_cc}" CFLAGS="%{uclibc_cflags}" ../configure --with-zlib --with-xz --enable-static --disable-shared --disable-tools
%make V=1
popd
%endif

# The extra --includedir gives us the possibility to detect dependent
# packages which fail to properly use pkgconfig.
%configure	--with-xz \
		--with-zlib \
		--includedir=%{_includedir}/%{name}-%{version} \
		--with-rootlibdir=/%{_lib} \
		--bindir=/bin \
		--enable-shared \
		--enable-static
%make

%install
%makeinstall_std
# Remove standalone tools
rm -f %{buildroot}/bin/kmod-*

# kmod-compat
mkdir -p %{buildroot}/{bin,sbin}
ln -s kmod %{buildroot}/bin/lsmod
for i in depmod insmod lsmod modinfo modprobe rmmod; do
	ln -s /bin/kmod %{buildroot}/sbin/$i
done;

%if %{with dietlibc}
install -m644 ./diet/libkmod/.libs/libkmod.a -D %{buildroot}%{_prefix}/lib/dietlibc/lib-%{_arch}/libkmod.a
%endif

%if %{with uclibc}
install -m644 ./uclibc/libkmod/.libs/libkmod.a -D %{buildroot}%{_prefix}/uclibc/%{_libdir}/libkmod.a
%endif

%check
make check

%files
/bin/kmod
%{_mandir}/man5/*
%{_mandir}/man8/*

%files -n %{libname}
/%{_lib}/libkmod.so.%{major}*

%files -n %{devname}
%{_includedir}/*
%{_libdir}/pkgconfig/*.pc
%{_libdir}/libkmod.so
%{_libdir}/libkmod.a
%if %{with dietlibc}
%{_prefix}/lib/dietlibc/lib-%{_arch}/libkmod.a
%endif
%if %{with uclibc}
%{_prefix}/uclibc/%{_libdir}/libkmod.a
%endif

%files compat
/bin/lsmod
/sbin/*
