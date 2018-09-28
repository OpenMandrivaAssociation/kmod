%define major 2
%define libname %mklibname %{name} %{major}
%define devname %mklibname %{name} -d

# (tpg) this is important
# keep this synchronized with module-init-tools-ver-rel+1
%define module_ver 3.17-1

Summary:	Utilities to load modules into the kernel
Name:		kmod
Version:	25
Release:	4
License:	LGPLv2.1+ and GPLv2+
Group:		System/Kernel and hardware
Url:		http://git.kernel.org/?p=utils/kernel/kmod/kmod.git;a=summary
# See also: http://packages.profusion.mobi/kmod/
Source0:	https://www.kernel.org/pub/linux/utils/kernel/kmod/%{name}-%{version}.tar.xz
Source1:	%{name}.rpmlintrc
# (tpg) provide config files from module-init-tools
Source2:	modprobe.default
Source3:	modprobe.preload
Source4:	blacklist-mdv.conf
Source5:	ipw-no-associate.conf
Source6:	blacklist-compat.conf
Source7:	usb.conf
Patch0:		kmod-21-allow-static.patch
Patch1:		kmod-25-libkmod.h-buildfix.patch
BuildRequires:	gtk-doc
BuildRequires:	xsltproc
BuildRequires:	pkgconfig(glib-2.0)
BuildRequires:	pkgconfig(gobject-2.0)
BuildRequires:	pkgconfig(liblzma)
BuildRequires:	pkgconfig(zlib)
Obsoletes:	module-init-tools < %{module_ver}
Provides:	module-init-tools = %{module_ver}
Conflicts:	kmod-compat < 18-5
%rename		kmod-compat

%description
kmod is a set of tools to handle common tasks with Linux kernel
modules like insert, remove, list, check properties, resolve
dependencies and aliases.

These tools are designed on top of libkmod, a library that is shipped
with kmod. The aim is to be compatible with tools, configurations and
indexes from module-init-tools project.

%package -n %{libname}
Summary:	Library to interact with Linux kernel modules
License:	LGPLv2.1+
Group:		System/Libraries
Requires:	%{name} = %{EVRD}
Conflicts:	%{mklibname modprobe 0} <= 3.6-18
Conflicts:	%{mklibname modprobe 1} < %{module_ver}

%description -n %{libname}
libkmod was created to allow programs to easily insert, remove and
list modules, also checking its properties, dependencies and aliases.

%package -n %{devname}
Summary:	Development files for libkmod
Group:		Development/C
License:	LGPLv2.1+
Requires:	%{libname} = %{EVRD}
Requires:	%{name} = %{EVRD}
Provides:	%{name}-devel = %{EVRD}

%description -n %{devname}
libkmod was created to allow programs to easily insert, remove and
list modules, also checking its properties, dependencies and aliases.

%prep
%autosetup -p1
aclocal -I m4
automake -a
autoconf

%build
# The extra --includedir gives us the possibility to detect dependent
# packages which fail to properly use pkgconfig.
%configure \
	--with-xz \
	--with-zlib \
	--includedir=%{_includedir}/%{name}-%{version} \
	--with-rootlibdir=/%{_lib} \
	--bindir=/bin \
	--enable-shared \
	--enable-gtk-doc \
	--enable-gtk-doc-html \
	--with-html-dir=%{_docdir}/%{name}/html

%make_build LIBS=-lpthread

%install
%make_install

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
install -m 644 %{SOURCE4} %{SOURCE5} %{SOURCE6} %{SOURCE7} %{buildroot}%{_sysconfdir}/modprobe.d
touch %{buildroot}%{_sysconfdir}/modprobe.conf

# (tpg) we still use this
ln -s ../modprobe.conf %{buildroot}%{_sysconfdir}/modprobe.d/01_mandriva.conf
ln -sf %{_includedir}/%{name}-%{version}/libkmod.h %{buildroot}/%{_includedir}/libkmod.h

# kmod-compat
mkdir -p %{buildroot}/{bin,sbin}
ln -s kmod %{buildroot}/bin/lsmod
ln -s kmod %{buildroot}/sbin/lsmod
for i in depmod insmod lsmod modinfo modprobe rmmod; do
    ln -s /bin/kmod %{buildroot}/sbin/$i
done;

#check
# make check suddenly seems to fail copy this directory from srcdir...
#[ ! -d glibc/testsuite ] && cp -a testsuite glibc
# make -C glibc check

%files
%dir %{_sysconfdir}/modprobe.d
%dir %{_sysconfdir}/depmod.d
%dir /lib/modprobe.d
%config(noreplace) %{_sysconfdir}/modprobe.preload
%config(noreplace) %{_sysconfdir}/modprobe.conf
%config(noreplace) %{_sysconfdir}/modprobe.d/*.conf
/bin/lsmod
/sbin/lsmod
/sbin/*
/bin/kmod
%{_datadir}/bash-completion/completions/kmod
%{_mandir}/man5/*
%{_mandir}/man8/*

%files -n %{libname}
/%{_lib}/libkmod.so.%{major}*

%files -n %{devname}
%doc %{_docdir}/%{name}
%{_includedir}/*
%{_libdir}/pkgconfig/*.pc
%{_libdir}/libkmod.so
