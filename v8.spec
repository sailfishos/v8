%ifarch mips aarch64
  %bcond_with gdbjit
%else
  %bcond_without gdbjit
%endif

Name:           v8
Version:        3.25.11
Release:        1%{?dist}
Summary:        JavaScript Engine
License:        BSD-3-Clause
Group:          System/Libraries
Url:            http://code.google.com/p/v8
Source0:        http://gsdview.appspot.com/chromium-browser-official/%{name}-%{version}.tar.bz2
Patch1:         fix-gcc48.patch
BuildRequires:  gcc-c++
BuildRequires:  lzma
BuildRequires:  python-devel
BuildRequires:  readline-devel
BuildRequires:  libicu-devel
%if %{with gdbjit}
BuildRequires:  gdb
%endif

%global somajor `echo %{version} | cut -f1 -d'.'`
%global sominor `echo %{version} | cut -f2 -d'.'`
%global sobuild `echo %{version} | cut -f3 -d'.'`
%global sover %{somajor}.%{sominor}.%{sobuild}

%ifarch i586 i486
%global target ia32
%endif
%ifarch x86_64
%global target x64
%endif
%ifarch armv6l armv6hl armv7l armv7hl armv7tnhl
%global target arm
%endif
%ifarch mipsel
%global target mipsel
%endif
%ifarch aarch64
%global target a64
%endif

%description
V8 is Google's open source JavaScript engine. V8 is written in C++ and is used
in Google Chrome, the open source browser from Google. V8 implements ECMAScript
as specified in ECMA-262, 3rd edition.

%package devel

Summary:        Development headers and libraries for v8
Group:          Development/Libraries
Requires:       %{name} = %{version}

%description devel
Development headers and libraries for v8.

%package bin

Summary:        Executables for V8
Group:          System/Libraries

%description bin
Executables for V8.

%package private-headers-devel

Summary:        Private Development headers for v8
Group:          Development/Libraries/C and C++
Requires:       %{name}-devel = %{version}

%description private-headers-devel
Special Private Development headers for v8.

%prep
%setup -q
%patch1 -p0

%build

env=CCFLAGS:"$RPM_OPT_FLAGS -fno-strict-aliasing -Wno-unused-parameter -Wno-unused-but-set-variable -fPIC"
MAKE_EXTRA_FLAGS=""

export ICU_LINK_FLAGS=`pkg-config --libs-only-l icu-i18n`

%ifarch armv6hl armv7hl armv7tnhl
MAKE_EXTRA_FLAGS+=hardfp=on
%endif

myconf+=" -Duse_system_icu=1
          -Dcomponent=shared_library
          -Dsoname_version=%{somajor}
          -Dconsole=readline"

%if %{with gdbjit}
myconf+=" -Dv8_enable_gdbjit=on"
%endif

%ifarch armv7tnhl
myconf+=" -Darm_neon=1 -Darm_fpu=neon"
%endif

myconf+=" -Dv8_target_arch=%{target}"

./build/gyp_v8 -f make build/all.gyp --depth=. -S.%{target}.release $myconf

cd out
make -f Makefile.%{target}.release \
     builddir=%{_builddir}/%{buildsubdir}/out/%{target}.release \
     snapshots=on \
     $MAKE_EXTRA_FLAGS \
     BUILDTYPE=Release V=1

%install
mkdir -p %{buildroot}%{_includedir}/v8/%{target}
mkdir -p %{buildroot}%{_libdir}
install -p include/*.h %{buildroot}%{_includedir}

install -p src/*.h %{buildroot}%{_includedir}/v8
install -p src/%{target}/*.h %{buildroot}%{_includedir}/v8/%{target}

install -p out/%{target}.release/lib.target/libv8.so* %{buildroot}%{_libdir}
mkdir -p %{buildroot}%{_bindir}
install -p -m0755 out/%{target}.release/d8 %{buildroot}%{_bindir}

# Various binaries
mkdir -p %{buildroot}%{_libexecdir}/v8
install -p -m0755 out/%{target}.release/cctest %{buildroot}%{_libexecdir}/v8
install -p -m0755 out/%{target}.release/shell %{buildroot}%{_libexecdir}/v8
install -p -m0755 out/%{target}.release/lineprocessor %{buildroot}%{_libexecdir}/v8
install -p -m0755 out/%{target}.release/process %{buildroot}%{_libexecdir}/v8

cd %{buildroot}%{_libdir}
ln -sf libv8.so.%{somajor} libv8.so

chmod -x %{buildroot}%{_includedir}/v8*.h

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%files
%defattr(-,root,root,-)
%doc AUTHORS ChangeLog LICENSE
%{_bindir}/d8
%{_libdir}/*.so.*
%exclude %{_libdir}/documentation.list

%files devel
%defattr(-,root,root,-)
%{_includedir}/*.h
%{_libdir}/*.so

%files bin
%defattr(-,root,root,-)
%{_libexecdir}/v8/

%files private-headers-devel
%defattr(644,root,root,-)
%{_includedir}/v8/
