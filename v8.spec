%global svncheckout 20101004svn5585

# For the 1.2 branch, we use 0s here
# For 1.3+, we use the three digit versions
%global somajor 2
%global sominor 4
%global sobuild 8
%global sover %{somajor}.%{sominor}.%{sobuild}

Name:		v8
Version:	%{somajor}.%{sominor}.%{sobuild}
Release:	1.%{svncheckout}%{?dist}
Summary:	JavaScript Engine
Group:		System Environment/Libraries
License:	BSD
URL:		http://code.google.com/p/v8
# No tarballs, pulled from svn
# Checkout script is Source1
Source0:	v8-%{version}-%{svncheckout}.tar.bz2
Source1:	v8-daily-tarball.sh
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
ExclusiveArch:	%{ix86} x86_64 %{arm}
BuildRequires:	scons, readline-devel

%description
V8 is Google's open source JavaScript engine. V8 is written in C++ and is used 
in Google Chrome, the open source browser from Google. V8 implements ECMAScript 
as specified in ECMA-262, 3rd edition.

%package devel
Group:		Development/Libraries
Summary:	Development headers and libraries for v8
Requires:	%{name} = %{version}-%{release}

%description devel
Development headers and libraries for v8.

%prep
%setup -q -n %{name}-%{version}-%{svncheckout}

# -fno-strict-aliasing is needed with gcc 4.4 to get past some ugly code
PARSED_OPT_FLAGS=`echo \'$RPM_OPT_FLAGS -fPIC -fno-strict-aliasing -Wno-unused-parameter\'| sed "s/ /',/g" | sed "s/',/', '/g"`
sed -i "s|'-O3',|$PARSED_OPT_FLAGS,|g" SConstruct
sed -i "s|'-Werror'|''|g" SConstruct

%build
export GCC_VERSION="44"
scons library=shared snapshots=on \
%ifarch x86_64
arch=x64 \
%endif
visibility=default \
env=CCFLAGS:"-fPIC"

# When will people learn to create versioned shared libraries by default?
# first, lets get rid of the old .so
rm -rf libv8.so
# Now, lets make it right.
%ifarch %{arm}
g++ $RPM_OPT_FLAGS -fPIC -o libv8.so.%{sover} -shared -Wl,-soname,libv8.so.%{somajor} obj/release/*.os obj/release/arm/*.os
%endif
%ifarch %{ix86}
g++ $RPM_OPT_FLAGS -fPIC -o libv8.so.%{sover} -shared -Wl,-soname,libv8.so.%{somajor} obj/release/*.os obj/release/ia32/*.os
%endif
%ifarch x86_64
g++ $RPM_OPT_FLAGS -fPIC -o libv8.so.%{sover} -shared -Wl,-soname,libv8.so.%{somajor} obj/release/*.os obj/release/x64/*.os
%endif

# We need to do this so d8 can link against it.
ln -sf libv8.so.%{sover} libv8.so

scons d8 \
%ifarch x86_64
arch=x64 \
%endif
library=shared snapshots=on console=readline visibility=default

# Sigh. I f*****g hate scons.
rm -rf d8

g++ $RPM_OPT_FLAGS -o d8 obj/release/d8-debug.os obj/release/d8-posix.os obj/release/d8-readline.os obj/release/d8.os obj/release/d8-js.os -lpthread -lreadline -lpthread -L. -lv8

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}%{_includedir}
mkdir -p %{buildroot}%{_libdir}
install -p include/*.h %{buildroot}%{_includedir}
install -p libv8.so.%{sover} %{buildroot}%{_libdir}
mkdir -p %{buildroot}%{_bindir}
install -p -m0755 d8 %{buildroot}%{_bindir}

pushd %{buildroot}%{_libdir}
ln -sf libv8.so.%{sover} libv8.so
ln -sf libv8.so.%{sover} libv8.so.%{somajor}
ln -sf libv8.so.%{sover} libv8.so.%{somajor}.%{sominor}

chmod -x %{buildroot}%{_includedir}/v8*.h
popd

%clean
rm -rf %{buildroot}

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%files
%defattr(-,root,root,-)
%doc AUTHORS ChangeLog LICENSE
%{_bindir}/d8
%{_libdir}/*.so.*

%files devel
%defattr(-,root,root,-)
%{_includedir}/*.h
%{_libdir}/*.so

