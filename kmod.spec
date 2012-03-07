%define	major	2
%define	libname	%mklibname %{name} %{major}
%define	devname	%mklibname %{name} -d

Name:		kmod
Summary:	Utilities to load modules into the kernel
Version:	5
Release:	2
License:	LGPLv2.1+ and GPLv2+
Group:		System/Kernel and hardware
Url:		http://www.politreco.com/2011/12/announce-kmod-2/

Source0:	http://packages.profusion.mobi/kmod/%{name}-%{version}.tar.xz
Source1:	http://packages.profusion.mobi/kmod/%{name}-%{version}.tar.sign

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
Summary:        Library to interact with Linux kernel modules
License:        LGPLv2.1+
Group:          System/Libraries

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
# The extra --includedir gives us the possibility to detect dependent
# packages which fail to properly use pkgconfig.
%configure	--with-xz \
		--with-zlib \
		--includedir=%{_includedir}/%{name}-%{version} \
		--with-rootlibdir=/%{_lib} \
		--bindir=/bin
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

%files compat
/bin/lsmod
/sbin/*
