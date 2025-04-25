%define major 2
%define oldlibname %mklibname %{name} 2
%define libname %mklibname %{name}
%define devname %mklibname %{name} -d

# (tpg) reduce size a little bit
%global optflags %{optflags} -Oz

Summary:	Utilities to load modules into the kernel
Name:		kmod
Version:	34.2
Release:	1
License:	LGPLv2.1+ and GPLv2+
Group:		System/Kernel and hardware
Url:		https://git.kernel.org/?p=utils/kernel/kmod/kmod.git;a=summary
# See also: http://packages.profusion.mobi/kmod/
Source0:	https://www.kernel.org/pub/linux/utils/kernel/kmod/%{name}-%{version}.tar.xz
Source1:	%{name}.rpmlintrc
# (tpg) provide config files from module-init-tools
Source2:	modprobe.default
Source4:	blacklist-omv.conf
Source5:	ipw-no-associate.conf
Source6:	usb.conf
Patch999:	kmod-21-allow-static.patch

BuildRequires:	scdoc
BuildRequires:	gtk-doc
BuildRequires:	xsltproc
BuildRequires:	pkgconfig(glib-2.0)
BuildRequires:	pkgconfig(gobject-2.0)
BuildRequires:	pkgconfig(liblzma)
BuildRequires:	pkgconfig(zlib)
BuildRequires:	pkgconfig(libzstd)
BuildRequires:	pkgconfig(openssl)
BuildRequires:	systemd-rpm-macros
Provides:	/sbin/modprobe
Conflicts:	kmod-compat < 18-5
%rename		kmod-compat
Recommends:	hwdata

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
%rename %{oldlibname}

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
autoreconf -fiv
# usrmerge... (not yet, kernel Makefiles hardcode /lib)
#find . -type f |xargs \
#	sed -i -e 's,/lib/modules,%{_prefix}/lib/modules,g'

%build
# The extra --includedir gives us the possibility to detect dependent
# packages which fail to properly use pkgconfig.
%configure \
	--with-openssl \
	--with-zstd \
	--with-xz \
	--with-zlib \
	--includedir=%{_includedir}/%{name}-%{version} \
	--enable-shared \
	--enable-gtk-doc \
	--disable-gtk-doc-html \
	--with-html-dir=%{_docdir}/%{name}/html

%make_build LIBS=-lpthread

%install
%make_install

rm -f %{buildroot}%{_libdir}/libkmod.la

# (tpg) install config files
install -d -m755 %{buildroot}%{_sysconfdir}
install -d -m755 %{buildroot}%{_sysconfdir}/depmod.d
install -d -m755 %{buildroot}%{_sysconfdir}/modprobe.d
install -d -m755 %{buildroot}%{_modprobedir}
install -m 644 %{SOURCE2} %{buildroot}%{_sysconfdir}/modprobe.d/00_modprobe.conf
install -m 644 %{SOURCE4} %{SOURCE5} %{SOURCE6} %{buildroot}%{_sysconfdir}/modprobe.d
install -m 644 %{SOURCE6} %{buildroot}%{_modprobedir}

ln -sf %{_includedir}/%{name}-%{version}/libkmod.h %{buildroot}/%{_includedir}/libkmod.h

#check
# make check suddenly seems to fail copy this directory from srcdir...
#[ ! -d glibc/testsuite ] && cp -a testsuite glibc
# make -C glibc check

%files
%dir %{_sysconfdir}/modprobe.d
%dir %{_sysconfdir}/depmod.d
%config(noreplace) %{_sysconfdir}/modprobe.d/*.conf
%config(noreplace) %{_prefix}/lib/modprobe.d/*.conf
# Listing files manually here instead of just packaging
# {_bindir}/* to make sure we get a hard error if the
# symlinks to the older names (insmod and friends)
# ever get removed
%{_bindir}/kmod
%{_bindir}/depmod
%{_bindir}/insmod
%{_bindir}/lsmod
%{_bindir}/modinfo
%{_bindir}/modprobe
%{_bindir}/rmmod
%doc %{_mandir}/man5/*
%doc %{_mandir}/man8/*
%{_datadir}/bash-completion/completions/*
%{_datadir}/fish/vendor_functions.d/*
%{_datadir}/zsh/site-functions/*

%files -n %{libname}
%{_libdir}/libkmod.so.%{major}*

%files -n %{devname}
%{_includedir}/*
%{_libdir}/pkgconfig/*.pc
%{_datadir}/pkgconfig/*.pc
%{_libdir}/libkmod.so

%ifarch %{aarch64}
%pre -p <lua>
-- FIXME
-- This really does not belong here. But something is preventing
-- /lib/ld-linux-aarch64.so.1 from being in the right place during
-- post-usrmerge installations.
-- Since kmod is the first package in a typical install that requires
-- ld-linux-aarch64.so.1 in the right place (post script), make sure
-- it exists here.
-- This should be removed once we know why the symlink goes away at
-- some point after installing glibc.
local s=posix.stat("/lib")
if s then
	print("/lib is a " .. s.type)
else
	print("/lib doesn't exist")
end
local s=posix.stat("/lib/ld-linux-aarch64.so.1")
if s then
	print("/lib/ld-linux-aarch64.so.1 is a " .. s.type)
else
	print("/lib/ld-linux-aarch64.so.1 doesn't exist")
	posix.symlink("/usr/lib64/ld-linux-aarch64.so.1", "/lib/ld-linux-aarch64.so.1")
	local s=posix.stat("/lib/ld-linux-aarch64.so.1")
	if s then
		print("FIXED, it's now a " .. s.type)
	else
		print("Not fixed")
	end
end
local s=posix.stat("/usr/lib64/ld-linux-aarch64.so.1")
if s then
	print("/usr/lib64/ld-linux-aarch64.so.1 is a " .. s.type)
else
	print("/usr/lib64/ld-linux-aarch64.so.1 doesn't exist")
end
%endif
