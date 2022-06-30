Name:             apkg-ex-minimal-no-git
Version:          {{ version }}
Release:          {{ release }}%{?dist}
Summary:          testing package containing a single script

License:          GPL 3.0
URL:              https://gitlab.nic.cz/packaging/apkg
Source0:          %{name}-v%{version}.tar.gz

BuildArch:        noarch

Requires:         bash

%description
This package is for apkg testing and only contains
a single-line bash script.

%prep
%autosetup -n %{name}-v%{version} -S git

%install
install -D -m 0755 %{name} %{buildroot}%{_bindir}/%{name}

%files
%doc README.md
%{_bindir}/%{name}

%changelog
* {{ now }} Jakub Ružička <jakub.ruzicka@nic.cz> - {{ version }}-{{ release }}
- upstream version {{ version }}
