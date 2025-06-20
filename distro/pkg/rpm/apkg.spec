Name:             apkg
Version:          {{ version }}
Release:          cznic.{{ release }}%{?dist}
Summary:          cross-distro packaging automation tool

License:          GPL 3.0
URL:              https://gitlab.nic.cz/packaging/apkg
Source0:          %{name}-v%{version}.tar.gz

BuildArch:        noarch

BuildRequires:    git-core
BuildRequires:    python3-devel
BuildRequires:    python3-setuptools

Requires:         git-core
Requires:         rpm-build
Requires:         python3-cached-property
Requires:         python3-click
Requires:         python3-distro
%if "x%{?suse_version}" == "x"
Requires:         python3-jinja2
%else
Requires:         python3-Jinja2
%endif
Requires:         python3-requests
%if 0%{?fedora} >= 40 || 0%{?rhel} >= 10
Requires:         python3-tomli-w
%else
Requires:         python3-toml
%endif
Recommends:       python3-blessed

Provides:         python3-%{name} = %{version}-%{release}

%description
Universal Free and Open Source minimalist cross-distro packaging automation
tool aimed at producing high quality packages for many different OS
distributions/packaging systems with minimum overhead.

%prep
%autosetup -n %{name}-v%{version} -S git
# blessed is in install_requires for PyPI, but it's optional for colors
sed -i '/blessed/d' pyproject.toml setup.cfg
# toml is in install_requires for PyPI for backward compat, but it's not
# available on modern fedora/el in favor of tomllib in Python >= 3.11 and tomli_w
sed -i '/"toml"/d' pyproject.toml
sed -i '/    toml/d' setup.cfg

%build
%py3_build

%install
%py3_install

%files
%doc README.md
%license COPYING
%{_bindir}/apkg
%{python3_sitelib}/apkg
%{python3_sitelib}/*.egg-info


%changelog
* {{ now }} Jakub Ružička <jakub.ruzicka@nic.cz> - {{ version }}-{{ release }}
- upstream version {{ version }}
