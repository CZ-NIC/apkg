Name:             apkg
Version:          {{ version }}
Release:          {{ release }}%{?dist}
Summary:          cross-distro packaging automation tool

License:          GPL 3.0
URL:              https://gitlab.nic.cz/packaging/apkg
Source0:          %{name}-v%{version}.tar.gz

BuildArch:        noarch

BuildRequires:    git-core

Requires:         python3-apkg == %{version}-%{release}

%description
Universal Free and Open Source minimalist cross-distro packaging automation
tool aimed at producing high quality packages for many different OS
distributions/packaging systems with minimum overhead.

This package contains apkg CLI executable.


%package -n python3-apkg
Summary:          cross-distro packaging automation tool

BuildRequires:    python3-devel
BuildRequires:    python3-setuptools

Requires:         git-core
Requires:         rpm-build

Requires:         python3-click
Requires:         python3-distro
%if "x%{?suse_version}" == "x"
Requires:         python3-jinja2
%else
Requires:         python3-Jinja2
%endif
Requires:         python3-requests
Requires:         python3-toml

%description -n python3-apkg
Universal Free and Open Source minimalist cross-distro packaging automation
tool aimed at producing high quality packages for many different OS
distributions/packaging systems with minimum overhead.

This package contains apkg module for Python 3.


%prep
%autosetup -n %{name}-v%{version} -S git

%build
%py3_build

%install
%py3_install

%files -n apkg
%doc README.md
%{_bindir}/apkg

%files -n python3-apkg
%doc README.md
%license COPYING
%{python3_sitelib}/apkg
%{python3_sitelib}/*.egg-info


%changelog
* {{ now }} Jakub Ružička <jakub.ruzicka@nic.cz> - {{ version }}-{{ release }}
- upstream version {{ version }}
