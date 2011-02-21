# Mainly inspired from Fedora's .spec

%define name    picosat
%define version 936
%define release %mkrel 0

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
Requires:       gzip, %{name}-libs = %{version}-%{release}

%description
The SAT problem is the classical NP complete problem of searching
for a satisfying assignment of a propositional formula in
conjunctive normal form (CNF). General information on SAT can be
found at http://www.satlive.org or http://www.satlib.org.

%package libs
Group:          Development/Libraries
Summary:        A SAT solver library

%description libs
The PicoSAT library, which contains routines that solve the SAT problem.
The library has a simple API which is similar to that of previous
solvers by the same authors.

%package devel
Group:          Development/Libraries
Summary:        Development files for PicoSAT
Requires:       %{name}-libs = %{version}-%{release}

%description devel
Headers and other development files for PicoSAT.

%prep
%setup -q

%build
# The configure script is NOT autoconf-generated and chooses its own CFLAGS,
# so we mimic its effects instead of using it.

# Build the version with trace support
sed -e "s/@CC@/gcc/" \
    -e "s/@CFLAGS@/${RPM_OPT_FLAGS} -DTRACE -DNDEBUG -fPIC/" \
    -e "s/-Xlinker libpicosat.so/-Xlinker libpicosat.so.0/" \
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
    -e "s/@CFLAGS@/${RPM_OPT_FLAGS} -DNDEBUG -fPIC/" \
    -e "s/-Xlinker libpicosat.so/-Xlinker libpicosat.so.0/" \
    -e "s/@TARGETS@/libpicosat.so picosat/" \
  makefile.in > makefile
make

%install
rm -rf $RPM_BUILD_ROOT
# Install the header file
mkdir -p $RPM_BUILD_ROOT%{_includedir}
cp -p picosat.h $RPM_BUILD_ROOT%{_includedir}

# Install the libraries
mkdir -p $RPM_BUILD_ROOT%{_libdir}
cp -p libpicosat-trace.so $RPM_BUILD_ROOT%{_libdir}/libpicosat-trace.so.0.0.%{version}
ln -s libpicosat-trace.so.0.0.%{version} $RPM_BUILD_ROOT%{_libdir}/libpicosat-trace.so.0
ln -s libpicosat-trace.so.0 $RPM_BUILD_ROOT%{_libdir}/libpicosat-trace.so
cp -p libpicosat.so $RPM_BUILD_ROOT%{_libdir}/libpicosat.so.0.0.%{version}
ln -s libpicosat.so.0.0.%{version} $RPM_BUILD_ROOT%{_libdir}/libpicosat.so.0
ln -s libpicosat.so.0 $RPM_BUILD_ROOT%{_libdir}/libpicosat.so

# Install the binaries
mkdir -p $RPM_BUILD_ROOT%{_bindir}
cp -p picosat picosat.trace picomus $RPM_BUILD_ROOT%{_bindir}

# Install the man pages
mkdir -p $RPM_BUILD_ROOT%{_mandir}/man1
cp -p %{SOURCE1} %{SOURCE2} %{SOURCE3} $RPM_BUILD_ROOT%{_mandir}/man1

%post libs -p /sbin/ldconfig

%postun libs -p /sbin/ldconfig

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

%files libs
%defattr(-,root,root,-)
%doc LICENSE NEWS
%{_libdir}/libpicosat-trace.so.*
%{_libdir}/libpicosat.so.*

%files devel
%defattr(-,root,root,-)
%{_includedir}/picosat.h
%{_libdir}/libpicosat-trace.so
%{_libdir}/libpicosat.so
