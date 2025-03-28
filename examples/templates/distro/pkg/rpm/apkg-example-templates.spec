%define EX_NAME apkg-example-templates

Name:             %{EX_NAME}
Version:          {{ version }}
Release:          {{ release }}%{?dist}
Summary:          minimal example of apkg templating system

License:          GPL 3.0
Source0:          %{name}-v%{version}.tar.gz

BuildArch:        noarch

%description
This is a minimal example of apkg templating features.

%prep
%autosetup -n %{name}-v%{version} -S git

%files
%doc README.md

%changelog
* {{ now }} Jakub Ružička <jakub.ruzicka@nic.cz> - {{ version }}-{{ release }}
- new upstream version {{ version }}
- distro: {{ distro }} / {{ distro.idver }} / {{ distro.tiny }}
- include: {% include 'distro/common/shared.txt' %}
- raw include: {% include_raw 'distro/common/shared.txt' %}
{%- if distro.match('fedora') %}
- Fedora-specific block
{%- elif distro.match('centos <= 7', 'rhel <= 7') %}
- only on EL 7 and older
{%- elif distro.match('el-8') %}
- only on EL 8 (distro alias)
{%- endif %}
