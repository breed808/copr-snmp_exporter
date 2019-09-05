# Run tests (requires network connectivity)
%global with_check 0

# Prebuilt binaries break build process for CentOS. Disable debug packages to resolve
%if 0%{?rhel}
%define debug_package %{nil}
%endif

%global provider        github
%global provider_tld    com
%global project         prometheus
%global repo            snmp_exporter
# https://github.com/prometheus/snmp_exporter/
%global provider_prefix %{provider}.%{provider_tld}/%{project}/%{repo}
%global import_path     %{provider_prefix}

Name:           golang-%{provider}-%{project}-%{repo}
Version:        0.15.0
Release:        1%{?dist}
Summary:        SNMP Exporter for Prometheus
License:        ASL 2.0
URL:            https://%{provider_prefix}
Source0:        https://%{provider_prefix}/archive/v%{version}.tar.gz
Source1:        snmp_exporter.service
Source2:        README.packager.txt

Provides:       snmp_exporter = %{version}-%{release}

%if 0%{?rhel} != 6
BuildRequires:  systemd
%endif

# e.g. el6 has ppc64 arch without gcc-go, so EA tag is required
ExclusiveArch:  %{?go_arches:%{go_arches}}%{!?go_arches:%{ix86} x86_64 aarch64 %{arm}}
# If go_compiler is not set to 1, there is no virtual provide. Use golang instead.
BuildRequires:  %{?go_compiler:compiler(go-compiler)}%{!?go_compiler:golang}
# Dependencies required by the generator tool.
BuildRequires: gcc
BuildRequires: gcc-c++
BuildRequires: net-snmp-devel

%description
This is an exporter that exposes information gathered from SNMP for use by the Prometheus monitoring system.

There are two components. An exporter that does the actual scraping, and a generator (which depends on NetSNMP) that creates the configuration for use by the exporter.

%prep
%setup -q -n %{repo}-%{version}

%build
# Required as %%{SOURCE} can't be included in %%doc directive
cp %{SOURCE2} .
export GO111MODULE=on
go build -ldflags=-linkmode=external -mod vendor -o snmp_exporter
cd generator
go build -ldflags=-linkmode=external -mod vendor -o snmp_generator

%install
%if 0%{?rhel} != 6
install -d -p   %{buildroot}%{_unitdir}
%endif

install -Dpm 0644 snmp.yml %{buildroot}%{_sysconfdir}/snmp_exporter/snmp.yml
install -Dpm 0644 generator/Makefile %{buildroot}%{_datadir}/snmp_exporter/Makefile
install -Dpm 0644 generator/generator.yml %{buildroot}%{_datadir}/snmp_exporter/generator.yml.example
install -Dpm 0755 snmp_exporter %{buildroot}%{_sbindir}/snmp_exporter
install -Dpm 0755 generator/snmp_generator %{buildroot}%{_bindir}/snmp_generator

%if 0%{?rhel} != 6
install -Dpm 0644 %{SOURCE1} %{buildroot}%{_unitdir}/snmp_exporter.service
%endif

%if 0%{?with_check}
%check
export GO111MODULE=on
go test -mod vendor
%endif


%files
%if 0%{?rhel} != 6
%{_unitdir}/snmp_exporter.service
%endif
%attr(0640, snmp_exporter, snmp_exporter) %config(noreplace) %{_sysconfdir}/snmp_exporter/snmp.yml
%license LICENSE
%doc README.md README.packager.txt
%{_sbindir}/snmp_exporter
%{_bindir}/snmp_generator
%{_datadir}/snmp_exporter

%pre
getent group snmp_exporter > /dev/null || groupadd -r snmp_exporter
getent passwd snmp_exporter > /dev/null || \
    useradd -rg snmp_exporter -s /sbin/nologin \
            -c "snmp Prometheus exporter" snmp_exporter

%post
%if 0%{?rhel} != 6
%systemd_post snmp_exporter.service
%endif

%preun
%if 0%{?rhel} != 6
%systemd_preun snmp_exporter.service
%endif

%postun
%if 0%{?rhel} != 6
%systemd_postun snmp_exporter.service
%endif

%changelog
