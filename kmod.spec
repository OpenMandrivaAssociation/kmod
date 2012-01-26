%define major 1
%define libname %mklibname %name %major
%define develname %mklibname %name -d
%define git_snapshot 0

Name:           kmod
Summary:        Utilities to load modules into the kernel
Version:        4
Release:        1
License:        LGPLv2.1+ and GPLv2+
Group:          System/Kernel and hardware
Url:            http://www.politreco.com/2011/12/announce-kmod-2/

Requires:	%libname = %version-%release

#Git-Clone:	git://git.profusion.mobi/kmod
Source:         %name-%version.tar.xz
Source1:	%name-%version.tar.sign

%if 0%{?git_snapshot}
BuildRequires:  autoconf automake libtool
%endif
BuildRequires:  pkgconfig >= 0.23 pkgconfig(liblzma) pkgconfig(zlib) xz

%description
kmod is a set of tools to handle common tasks with Linux kernel
modules like insert, remove, list, check properties, resolve
dependencies and aliases.

These tools are designed on top of libkmod, a library that is shipped
with kmod. The aim is to be compatible with tools, configurations and
indexes from module-init-tools project.

%package compat
Summary:        Compat symlinks for kernel module utilities
License:        GPLv2+
Group:          System/Kernel and hardware
Conflicts:      module-init-tools
Requires:	%name = %version-%release
Requires:	%libname = %version-%release

%description compat
kmod is a set of tools to handle common tasks with Linux kernel
modules like insert, remove, list, check properties, resolve
dependencies and aliases.

This package contains traditional name symlinks (lsmod, etc.)

%package -n %libname
Summary:        Library to interact with Linux kernel modules
License:        LGPLv2.1+
Group:          System/Libraries

%description -n %libname
libkmod was created to allow programs to easily insert, remove and
list modules, also checking its properties, dependencies and aliases.

%package -n %develname
Summary:        Development files for libkmod
Group:          Development/C
License:        LGPLv2.1+
Requires:       %libname = %version-%release

%description -n %develname
libkmod was created to allow programs to easily insert, remove and
list modules, also checking its properties, dependencies and aliases.

%prep
%setup -q

%build
%if 0%{?git_snapshot}
if [ ! -e configure ]; then
	autoreconf -fi;
fi;
%endif
# The extra --includedir gives us the possibility to detect dependent
# packages which fail to properly use pkgconfig.
%configure --with-xz --with-zlib --includedir=%_includedir/%name-%version \
	--with-rootlibdir=/%_lib --bindir=/bin
make %{?_smp_mflags}

%install
b="%buildroot";
%make_install
# Remove standalone tools
rm -f "$b/bin"/kmod-*;
rm -f "$b/%_libdir"/*.la;

# kmod-compat
mkdir -p "$b/bin" "$b/sbin";
ln -s kmod "$b/bin/lsmod";
for i in depmod insmod lsmod modinfo modprobe rmmod; do
	ln -s "/bin/kmod" "$b/sbin/$i";
done;

%check
make check

%post -n %libname -p /sbin/ldconfig

%postun -n %libname -p /sbin/ldconfig

%files
%defattr(-,root,root)
/bin/kmod

%files -n %libname
%defattr(-,root,root)
/%_lib/libkmod.so.1*

%files -n %develname
%defattr(-,root,root)
%_includedir/*
%_libdir/pkgconfig/*.pc
%_libdir/libkmod.so

%files compat
%defattr(-,root,root)
/bin/lsmod
/sbin/*
