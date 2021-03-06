Name:           perl-HTTP-Tiny
Version:        0.033
Release:        3%{?dist}
Summary:        Small, simple, correct HTTP/1.1 client
License:        GPL+ or Artistic
Group:          Development/Libraries
URL:            http://search.cpan.org/dist/HTTP-Tiny/
Source0:        http://www.cpan.org/authors/id/D/DA/DAGOLDEN/HTTP-Tiny-%{version}.tar.gz
# Check for write failure, bug #1031096,
# <https://github.com/chansen/p5-http-tiny/issues/32>
Patch0:         HTTP-Tiny-0.038-Croak-on-failed-write-into-a-file.patch
# Do not use already existing temporary files, bug #1031096,
# <https://github.com/chansen/p5-http-tiny/issues/32>
Patch1:         HTTP-Tiny-0.033-Do-not-use-already-existing-temporary-files.patch
BuildArch:      noarch
BuildRequires:  perl
BuildRequires:  perl(ExtUtils::MakeMaker) >= 6.30
BuildRequires:  perl(strict)
BuildRequires:  perl(warnings)
# Run-time:
BuildRequires:  perl(bytes)
BuildRequires:  perl(Carp)
BuildRequires:  perl(Errno)
BuildRequires:  perl(Fcntl)
BuildRequires:  perl(IO::Socket)
# IO::Socket::SSL 1.56 is optional
# Mozilla::CA is optional
# Net::SSLeay 1.49 is optional
BuildRequires:  perl(Time::Local)
# Tests:
BuildRequires:  perl(File::Basename) 
BuildRequires:  perl(File::Find)
BuildRequires:  perl(File::Spec)
BuildRequires:  perl(File::Spec::Functions)
BuildRequires:  perl(File::Temp)
BuildRequires:  perl(Exporter)
BuildRequires:  perl(IO::Dir)
BuildRequires:  perl(IO::File)
BuildRequires:  perl(List::Util)
BuildRequires:  perl(open)
BuildRequires:  perl(Test::More) >= 0.96
# On-line tests:
BuildRequires:  perl(IO::Socket::INET)
BuildRequires:  perl(IPC::Cmd)
BuildRequires:  perl(Data::Dumper)
Requires:       perl(:MODULE_COMPAT_%(eval "`perl -V:version`"; echo $version))
Requires:       perl(bytes)
Requires:       perl(Time::Local)

%description
This is a very simple HTTP/1.1 client, designed for doing simple GET requests
without the overhead of a large framework like LWP::UserAgent.

It is more correct and more complete than HTTP::Lite. It supports proxies
(currently only non-authenticating ones) and redirection. It also correctly
resumes after EINTR.

%prep
%setup -q -n HTTP-Tiny-%{version}
%patch0 -p1
%patch1 -p1

%build
perl Makefile.PL INSTALLDIRS=vendor
make %{?_smp_mflags}

%install
make pure_install DESTDIR=$RPM_BUILD_ROOT
find $RPM_BUILD_ROOT -type f -name .packlist -exec rm -f {} \;
%{_fixperms} $RPM_BUILD_ROOT/*

%check
make test

%files
%doc Changes CONTRIBUTING eg LICENSE README
%{perl_vendorlib}/*
%{_mandir}/man3/*

%changelog
* Fri Dec 27 2013 Daniel Mach <dmach@redhat.com> - 0.033-3
- Mass rebuild 2013-12-27

* Wed Nov 27 2013 Petr Pisar <ppisar@redhat.com> - 0.033-2
- Croak on failed write into a file (bug #1031096)
- Do not use already existing temporary files (bug #1031096)

* Mon Jun 24 2013 Petr Pisar <ppisar@redhat.com> - 0.033-1
- 0.033 bump

* Fri Jun 21 2013 Petr Pisar <ppisar@redhat.com> - 0.032-1
- 0.032 bump

* Thu Jun 20 2013 Petr Pisar <ppisar@redhat.com> - 0.031-1
- 0.031 bump

* Fri Jun 14 2013 Petr Pisar <ppisar@redhat.com> - 0.030-1
- 0.030 bump

* Thu Apr 18 2013 Petr Pisar <ppisar@redhat.com> - 0.029-1
- 0.029 bump

* Fri Mar 15 2013 Petr Pisar <ppisar@redhat.com> 0.028-1
- Specfile autogenerated by cpanspec 1.78.
