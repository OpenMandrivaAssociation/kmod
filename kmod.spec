%define	major	2
%define	libname	%mklibname %{name} %{major}
%define	devname	%mklibname %{name} -d

%bcond_without	dietlibc
%bcond_without	uclibc

Name:		kmod
Summary:	Utilities to load modules into the kernel
Version:	8
Release:	5
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
BuildRequires:	uClibc-devel >= 0.9.33.2-5
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
		--with-xz \
		--with-zlib \
		--with-rootlibdir=%{_prefix}/lib/dietlibc/lib-%{_arch} \
		--enable-static \
		--disable-shared \
		--disable-tools \
		--disable-silent-rules \
		CC="diet gcc" \
		LD="diet ld"
%make
popd
%endif

%if %{with uclibc}
mkdir -p uclibc
pushd uclibc
CFLAGS="%{uclibc_cflags}" \
%configure2_5x	--prefix=%{uclibc_root} \
		--with-xz \
		--with-zlib \
		--with-rootlibdir=%{uclibc_root}/%{_lib} \
		--enable-static \
		--enable-shared \
		--disable-tools \
		--disable-silent-rules \
		CC=%{uclibc_cc}
%make V=1
popd
%endif

mkdir -p glibc
pushd glibc
# The extra --includedir gives us the possibility to detect dependent
# packages which fail to properly use pkgconfig.
%configure	--with-xz \
		--with-zlib \
		--includedir=%{_includedir}/%{name}-%{version} \
		--with-rootlibdir=/%{_lib} \
		--bindir=/bin \
		--enable-shared \
		--enable-static \
		--disable-silent-rules
%make
popd

%install
%if %{with uclibc}
%makeinstall_std -C uclibc
%endif
%if %{with dietlibc}
%makeinstall_std -C uclibc
%endif
%makeinstall_std -C glibc
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
