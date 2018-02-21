%ifarch i686
%define karch i686
%endif
%ifarch x86_64
%define karch x86_64
%endif

# Redefine 'build_variant' at build time to create a kernel package named
# something like 'kernel-uek-dtrace'.
%define variant %{?build_variant:%{build_variant}}%{!?build_variant:-uek}

# Set this to the version of the kernel this module is compiled against.
%define kver %{?build_kver:{build_kver}}%{!?build_kver:3.8.13-16.el6uek}

# Increment this whenever the DTrace/userspace interface changes in an
# incompatible way.
%define dtrace_kernel_interface 1

Name: dtrace-modules-%{kver}
Summary: dtrace module
Version: 0.4.0
Release: 1.el6
Provides: dtrace-kernel-interface = %{dtrace_kernel_interface}
License: CDDL
Group: System Environment/Kernel
Requires: kernel%{variant} = %{kver}
Source0: dtrace-module-%{kver}.tar.bz2
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires: kernel%{variant}-devel = %{kver}
BuildRequires: libdtrace-ctf
ExclusiveArch: x86_64

%description
DTrace kernel modules.

This package contains the DTrace core module, and standard provider modules:
dtrace, profile, syscall, sdt (io, proc,sched), and fasttrap (USDT).

Maintainers:
------------
Nick Alcock <nick.alcock@oracle.com>
Kris van Hees <kris.van.hees@oracle.com>

%package headers
Summary:	Header files for communication with the DTrace kernel module.
Requires:	dtrace-modules-%{kver}
Provides:	dtrace-modules-headers = %{dtrace_kernel_interface}
%description headers
This package contains header files describing the protocol used by userspace to
communicate with the DTrace kernel module.

%package provider-headers
Summary:	Header files for implementation of DTrace providers.
Requires:	dtrace-modules-headers = %{dtrace_kernel_interface}
Provides:	dtrace-modules-provider-headers = %{dtrace_kernel_interface}
%description provider-headers
This package contains header files defining the API used to implement DTrace
providers.

%prep
rm -rf %{BuildRoot}

%setup -c -n %{name}

%build
cd dtrace
KSRC=/usr/src/kernels/%{kver}.%{karch}
make KERNELDIR=$KSRC karch=%{karch} modules

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/lib/modules/%{kver}.%{karch}/kernel/drivers/dtrace
install -m0644 ${RPM_BUILD_DIR}/%{name}/dtrace/*.ko %{buildroot}/lib/modules/%{kver}.%{karch}/kernel/drivers/dtrace/
mkdir -p %{buildroot}/usr/share/doc/dtrace-modules-%{kver}
install -m0644 ${RPM_BUILD_DIR}/%{name}/dtrace/NEWS %{buildroot}/usr/share/doc/dtrace-modules-%{kver}
cd dtrace
KSRC=/usr/src/kernels/%{kver}.%{karch}
make KERNELDIR=$KSRC karch=%{karch} headers_install INSTALL_HDR_PATH=%{buildroot}

%post
depmod -a %{kver}.%{karch} > /dev/null 2> /dev/null

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
/lib
/usr/share/doc

%files headers
%defattr(-,root,root,-)
/usr/include/linux/dtrace
%exclude /usr/include/linux/dtrace/provider*.h
%exclude /usr/include/linux/dtrace/types.h

%files provider-headers
%defattr(-,root,root,-)
/usr/include/linux/dtrace/provider*.h
/usr/include/linux/dtrace/types.h

%changelog
* Wed Aug  7 2013 Kris Van Hees <kris.van.hees@oracle.com> - 0.4.0-1
- Bugfix for module unloading.
- Support meta-providers, USDT, and fasttrap (for USDT only).
- Export DTrace kernel headers to userspace.
- Reimplemented ustack().
- Bugfixes.
* Mon Sep 17 2012 Kris Van Hees <kris.van.hees@oracle.com> - 0.3.0-2
- Remove development-only providers because they should not be built/released.
* Fri Sep 14 2012 Kris Van Hees <kris.van.hees@oracle.com> - 0.3.0
- Release of the DTrace kernel modules for UEK2 2.6.39-201.0.1 (DTrace kernel).
* Mon Mar 19 2012 Nick Alcock <nick.alcock@oracle.com> - 0.2.5-2
- Fix typo causing unconditional depmod at postinstall time
* Tue Mar 13 2012 Nick Alcock <nick.alcock@oracle.com> - 0.2.5
- New kernel, new userspace: no module changes.
* Wed Feb 15 2012 Kris van Hees <kris.van.hees@oracle.com> - 0.2.4
- Ban unloading of in-use dtrace modules while dtrace is running.
* Thu Feb  9 2012 Nick Alcock <nick.alcock@oracle.com> - 0.2.3
- There is one new DTrace option now, used internally by the
  testsuite.
* Tue Feb  7 2012 Kris Van Hees <kris.van.hees@oracle.com> - 0.2.2
- Switch MUTEX_HELD() from using mutex_is_locked() to new mutex_owned().
* Mon Jan 23 2012 Kris Van Hees <kris.van.hees@oracle.com> - 0.2.1
- Ensure that allocation attempts are done in atomic fashion so that a failing
  allocation attempt won't interfere with other allocations.
- Surpress OOM warnings.
* Mon Jan 23 2012 Kris Van Hees <kris.van.hees@oracle.com> - 0.2.0
- Release of the DTrace kernel modules for UEK2 2.6.39-101.0.1 (DTrace kernel).
* Wed Oct 19 2011 Kris Van Hees <kris.van.hees@oracle.com> - 0.1.0-1.el6
- Disable stub-based syscalls in the release pending merging in fixes.
* Thu Sep 29 2011 Maxim Uvarov <maxim.uvarov@oracle.com> - 0.1
- Initial release.
