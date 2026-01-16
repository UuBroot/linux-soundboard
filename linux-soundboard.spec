Name:           linux-soundboard
Version:        0.1.0
Release:        1%{?dist}
Summary:        A soundboard application for Linux

License:        MIT
URL:            https://github.com/uubroot/linux-soundboard
Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  meson >= 0.59.0
BuildRequires:  python3-devel
BuildRequires:  python3-pyside6
BuildRequires:  python3-soundfile
BuildRequires:  python3-numpy
BuildRequires:  python3-platformdirs

Requires:       python3
Requires:       python3-pyside6
Requires:       python3-soundfile
Requires:       python3-numpy
Requires:       python3-platformdirs
Requires:       pipewire
# python3-pynput is often not available in official repos, so it's commented out.
# Ensure it is installed via pip if not available as RPM.
# Requires:       python3-pynput

%description
A simple soundboard application for Linux using PipeWire.

%prep
%autosetup

%build
%meson
%meson_build

%install
%meson_install

%files
%{_bindir}/com.uubroot.Soundboard
%{_libdir}/soundboard/
%{_datadir}/applications/com.uubroot.Soundboard.desktop
%{_datadir}/metainfo/com.uubroot.Soundboard.metainfo.xml
%{_datadir}/icons/hicolor/256x256/apps/com.uubroot.Soundboard.png

%changelog
* Fri Jan 16 2026 Junie <junie@jetbrains.com> - 0.1.0-1
- Initial RPM release
