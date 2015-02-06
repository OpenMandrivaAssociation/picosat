# Mainly inspired from Fedora's .spec

%define name    picosat
%define version 936
%define major	1
%define release 7
%define	libname %mklibname %{name} %{major}
%define	libnamedevel %mklibname %{name} -d

Name:           %{name}
Summary:        Lightweight SAT solver
Version:        %{version}
Release:        %{release}
Source0:        http://fmv.jku.at/%{name}/%{name}-%{version}.tar.gz
URL:            http://fmv.jku.at/picosat/
# Thanks to David Wheeler for the man page.
Source1:        picosat.1
# Man page link for picosat.trace
Source2:        picosat.trace.1
# Man page for picomus
Source3:        picomus.1
# This patch has not been sent upstream.  It is specific to Fedora's build of
# two distinct binaries, one with trace support and one without.
Patch0:         picosat-trace.patch

Group:          Sciences/Computer science
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-buildroot
License:        MIT-like
# gzip required (see app.c); find-requires can't see into C code to find it
Requires:       gzip, %{libname} = %{version}-%{release}

%description
The SAT problem is the classical NP complete problem of searching
for a satisfying assignment of a propositional formula in
conjunctive normal form (CNF). General information on SAT can be
found at http://www.satlive.org or http://www.satlib.org.

%package -n	%{libname}
Group:          Development/C
Summary:        A SAT solver library

%description -n	%{libname}
The PicoSAT library, which contains routines that solve the SAT problem.
The library has a simple API which is similar to that of previous
solvers by the same authors.

%package -n	%{name}-devel
Group:          Development/C
Summary:        Development files for PicoSAT
Requires:       %{libname} = %{version}-%{release}

%description -n	%{name}-devel
Headers and other development files for PicoSAT.

%prep
%setup -q
%patch0 -p0

%build
# The configure script is NOT autoconf-generated and chooses its own CFLAGS,
# so we mimic its effects instead of using it.

# Build the version with trace support
sed -e "s/@CC@/gcc/" \
    -e "s/@CFLAGS@/${RPM_OPT_FLAGS} -DTRACE -DNDEBUG/" \
    -e "s/-Xlinker libpicosat.so/-Xlinker libpicosat.so.%{major}/" \
    -e "s/libpicosat/libpicosat-trace/g" \
    -e "s/-lpicosat/-lpicosat-trace/g" \
    -e "s/@TARGETS@/libpicosat-trace.so picosat picomus/" \
  makefile.in > makefile
make
mv picosat picosat.trace

# Build the fast version.
# Note that picomus needs trace support, so we don't rebuild it.
rm -f *.o *.s config.h
sed -e "s/@CC@/gcc/" \
    -e "s/@CFLAGS@/${RPM_OPT_FLAGS} -DNDEBUG/" \
    -e "s/-Xlinker libpicosat.so/-Xlinker libpicosat.so.%{major}/" \
    -e "s/@TARGETS@/libpicosat.so picosat/" \
  makefile.in > makefile
make

%install
rm -rf $RPM_BUILD_ROOT
# Install the header file
mkdir -p $RPM_BUILD_ROOT%{_includedir}/%{name}
cp -p picosat.h $RPM_BUILD_ROOT%{_includedir}/%{name}

# Install the libraries
mkdir -p $RPM_BUILD_ROOT%{_libdir}
cp -p libpicosat-trace.so $RPM_BUILD_ROOT%{_libdir}/libpicosat-trace.so.%{major}.0.%{version}
ln -s libpicosat-trace.so.%{major}.0.%{version} $RPM_BUILD_ROOT%{_libdir}/libpicosat-trace.so.%{major}
ln -s libpicosat-trace.so.%{major} $RPM_BUILD_ROOT%{_libdir}/libpicosat-trace.so
cp -p libpicosat.so $RPM_BUILD_ROOT%{_libdir}/libpicosat.so.%{major}.0.%{version}
ln -s libpicosat.so.%{major}.0.%{version} $RPM_BUILD_ROOT%{_libdir}/libpicosat.so.%{major}
ln -s libpicosat.so.%{major} $RPM_BUILD_ROOT%{_libdir}/libpicosat.so

# Install the binaries
mkdir -p $RPM_BUILD_ROOT%{_bindir}
cp -p picosat picosat.trace picomus $RPM_BUILD_ROOT%{_bindir}

# Install the man pages
mkdir -p $RPM_BUILD_ROOT%{_mandir}/man1
cp -p %{SOURCE1} %{SOURCE2} %{SOURCE3} $RPM_BUILD_ROOT%{_mandir}/man1

%post -n %{libname} -p /sbin/ldconfig
%postun -n %{libname} -p /sbin/ldconfig

%clean
rm -rf $RPM_BUILD_ROOT

# The LICENSE file is placed in the -libs package rather than the base package,
# because the -libs package is always installed when the base package is
# installed, but not vice versa.
%files
%defattr(-,root,root,-)
%{_bindir}/picosat*
%{_bindir}/picomus
%{_mandir}/man1/picosat*
%{_mandir}/man1/picomus*

%files -n %{libname}
%defattr(-,root,root,-)
%doc LICENSE NEWS
%{_libdir}/libpicosat-trace.so.*
%{_libdir}/libpicosat.so.*

%files -n %{name}-devel
%defattr(-,root,root,-)
%{_includedir}/%{name}/picosat.h
%{_libdir}/libpicosat-trace.so
%{_libdir}/libpicosat.so


%changelog
* Sun Feb 27 2011 Funda Wang <fwang@mandriva.org> 936-6mdv2011.0
+ Revision: 640458
- rebuild to obsolete old packages

* Tue Feb 22 2011 Alexandre Lissy <alissy@mandriva.com> 936-5
+ Revision: 639278
- Fixing compilation issues and trace patch not being applied

* Mon Feb 21 2011 Alexandre Lissy <alissy@mandriva.com> 936-4
+ Revision: 639143
- fixes major to 1 (as debian)
- fixing install directory of picosat.h as <picosat/picosat.h>

* Mon Feb 21 2011 Alexandre Lissy <alissy@mandriva.com> 936-3
+ Revision: 639137
- Fixes the dependency on library package
- Fixing -devel package name
- Using major for library version

* Mon Feb 21 2011 Alexandre Lissy <alissy@mandriva.com> 936-2
+ Revision: 639126
- Improving packaging for libraries using libname defines
- Fixing the Group for -devel package
- Fixing build issue with make -j
- Fixing typo in RPM group
- Adding picosat package.
- Created package structure for picosat.

