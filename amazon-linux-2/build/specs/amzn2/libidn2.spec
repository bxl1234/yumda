Summary:          Library to support IDNA2008 internationalized domain names
Name:             libidn2
Version:          2.0.4
Release: 1%{?dist}.0.2
License:          (GPLv2+ or LGPLv3+) and GPLv3+
Group:            System Environment/Libraries
URL:              https://www.gnu.org/software/libidn/#libidn2
Source0:          https://ftp.gnu.org/gnu/libidn/%{name}-%{version}.tar.gz
Source1:          https://ftp.gnu.org/gnu/libidn/%{name}-%{version}.tar.gz.sig
Patch0:           libidn2-2.0.0-rpath.patch
BuildRequires:    libunistring-devel
Requires(post):   /sbin/install-info, /sbin/ldconfig
Requires(preun):  /sbin/install-info
Requires(postun): /sbin/ldconfig
Provides:         bundled(gnulib)
BuildRoot:        %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

%description
Libidn2 is an implementation of the IDNA2008 specifications in RFC
5890, 5891, 5892, 5893 and TR46 for internationalized domain names
(IDN). It is a standalone library, without any dependency on libidn.

%package devel
Summary:          Development files for libidn2
Group:            Development/Libraries
Requires:         %{name}%{?_isa} = %{version}-%{release}, pkgconfig

%description devel
The libidn2-devel package contains libraries and header files for
developing applications that use libidn2.

%prep
%setup -q
%patch0 -p1 -b .rpath
touch -c -r configure.rpath configure
touch -c -r m4/libtool.m4.rpath m4/libtool.m4

%build
%configure --disable-static
make %{?_smp_mflags}

%install
rm -rf $RPM_BUILD_ROOT
make DESTDIR=$RPM_BUILD_ROOT INSTALL='install -p' install

# Clean-up examples for documentation
make %{?_smp_mflags} -C examples distclean
rm -f examples/Makefile*

# Don't install any libtool .la files
rm -f $RPM_BUILD_ROOT%{_libdir}/*.la

# Some file cleanups
rm -f $RPM_BUILD_ROOT%{_datadir}/info/dir

%check
make %{?_smp_mflags} -C tests check

%post
/sbin/ldconfig
/sbin/install-info %{_infodir}/%{name}.info.gz %{_infodir}/dir || :

%preun
if [ $1 = 0 ]; then
    /sbin/install-info --delete %{_infodir}/%{name}.info.gz %{_infodir}/dir || :
fi

%postun -p /sbin/ldconfig

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%{!?_licensedir:%global license %%doc}
%license COPYING COPYING.LESSERv3 COPYING.unicode COPYINGv2
%doc AUTHORS NEWS README.md
%{_bindir}/idn2
%{_mandir}/man1/idn2.1*
%{_libdir}/%{name}.so.*
%{_infodir}/%{name}.info*

%files devel
%defattr(-,root,root,-)
%doc doc/%{name}.html examples
%{_libdir}/%{name}.so
%{_libdir}/pkgconfig/%{name}.pc
%{_includedir}/*.h
%{_mandir}/man3/*
%{_datadir}/gtk-doc/

%changelog
* Wed Aug 30 2017 Robert Scheck <robert@fedoraproject.org> 2.0.4-1
- Upgrade to 2.0.4 (#1486881, #1486882)

* Tue Aug 01 2017 Robert Scheck <robert@fedoraproject.org> 2.0.3-1
- Upgrade to 2.0.3 (#1468608, #1474324)

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2.0.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Sun Apr 30 2017 Robert Scheck <robert@fedoraproject.org> 2.0.2-1
- Upgrade to 2.0.2 (#1444712)

* Thu Apr 06 2017 Robert Scheck <robert@fedoraproject.org> 2.0.0-1
- Upgrade to 2.0.0 (#1439727)

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.16-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Fri Jan 27 2017 Robert Scheck <robert@fedoraproject.org> 0.16-1
- Upgrade to 0.16 (#1416642)

* Mon Nov 21 2016 Robert Scheck <robert@fedoraproject.org> 0.11-1
- Upgrade to 0.11
- Reflect dual-licensing of library in license tag (#1397021)

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 0.10-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Mon Dec 7 2015 Than Ngo <than@redhat.com> 0.10-2
- fix build failure related to missing automake-1.14

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.10-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Sat Feb 21 2015 Till Maas <opensource@till.name> - 0.10-2
- Rebuilt for Fedora 23 Change
  https://fedoraproject.org/wiki/Changes/Harden_all_packages_with_position-independent_code

* Sun Oct 12 2014 Robert Scheck <robert@fedoraproject.org> 0.10-1
- Upgrade to 0.10

* Sun Aug 17 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.8-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.8-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.8-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.8-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Fri Nov 16 2012 Robert Scheck <robert@fedoraproject.org> 0.8-3
- Added provide bundled(gnulib) as it's a copylib (#821769)

* Thu Jul 19 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.8-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Sun Jan 15 2012 Robert Scheck <robert@fedoraproject.org> 0.8-1
- Upgrade to 0.8

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.7-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Sat Aug 13 2011 Robert Scheck <robert@fedoraproject.org> 0.7-1
- Upgrade to 0.7

* Sat Jun 04 2011 Robert Scheck <robert@fedoraproject.org> 0.6-1
- Upgrade to 0.6

* Wed May 18 2011 Robert Scheck <robert@fedoraproject.org> 0.5-1
- Upgrade to 0.5

* Mon May 16 2011 Robert Scheck <robert@fedoraproject.org> 0.4-1
- Upgrade to 0.4

* Sat May 07 2011 Robert Scheck <robert@fedoraproject.org> 0.3-1
- Upgrade to 0.3
- Initial spec file for Fedora and Red Hat Enterprise Linux
