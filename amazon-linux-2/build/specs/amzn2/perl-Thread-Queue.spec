Name:           perl-Thread-Queue
Version:        3.02
Release:        2%{?dist}
Summary:        Thread-safe queues
License:        GPL+ or Artistic
Group:          Development/Libraries
URL:            http://search.cpan.org/dist/Thread-Queue/
Source0:        http://www.cpan.org/authors/id/J/JD/JDHEDDEN/Thread-Queue-%{version}.tar.gz
BuildArch:      noarch
BuildRequires:  perl
BuildRequires:  perl(ExtUtils::MakeMaker)
BuildRequires:  perl(strict)
BuildRequires:  perl(warnings)
# Run-time:
BuildRequires:  perl(Carp)
BuildRequires:  perl(Scalar::Util) >= 1.10
BuildRequires:  perl(threads::shared) >= 1.21
# Tests:
BuildRequires:  perl(Config)
BuildRequires:  perl(Exporter)
BuildRequires:  perl(Test::More) >= 0.50
BuildRequires:  perl(Thread::Semaphore)
BuildRequires:  perl(threads)
Requires:       perl(:MODULE_COMPAT_%(eval "`perl -V:version`"; echo $version))
Requires:       perl(Carp)

%global __requires_exclude_from %{?__requires_exclude_from:%__requires_exclude_from|}%{_datadir}/doc/

%description
This module provides thread-safe FIFO queues that can be accessed safely by
any number of threads.

%prep
%setup -q -n Thread-Queue-%{version}

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
%doc Changes examples README
%{perl_vendorlib}/*
%{_mandir}/man3/*

%changelog
* Fri Dec 27 2013 Daniel Mach <dmach@redhat.com> - 3.02-2
- Mass rebuild 2013-12-27

* Fri Mar 01 2013 Petr Pisar <ppisar@redhat.com> - 3.02-1
- 3.02 bump

* Thu Feb 14 2013 Petr Pisar <ppisar@redhat.com> 3.01-1
- Specfile autogenerated by cpanspec 1.78.
