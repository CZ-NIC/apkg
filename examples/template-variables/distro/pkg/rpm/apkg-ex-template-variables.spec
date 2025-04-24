Name:             apkg-ex-template-variables
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
- upstream version {{ version }} for {{ distro }}
- custom variables: {{ custom_int }}, {{ custom_float }}, {{ custom_bool }}, {{ custom_str }}
- custom functions: 1 + 2 == {{ custom_fun_add(1, 2) }}, {{ custom_fun_echo('ECHO') }}
{%- if distro_like %}
- distro is like: {{ distro_like.names | join(', ') }}
{%- if distro_like.match('fedora') %}
  - fedora-like distro
{%- endif %}
{%- if distro_like.match('rhel') %}
  - rhel-like distro
{%- endif %}
{%- else %}
- distro_like is unavailable - probably building for different distro than host
{%- endif %}
