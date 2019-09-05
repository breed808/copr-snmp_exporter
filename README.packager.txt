Due to the dynamic nature of the SNMP configuration, some post-install steps are required by the systems administrator.
The snmp_generator tool must be used to generate a configuration file for use by the snmp_exporter system binary.

Copy the Makefile from /usr/share/snmp_exporter/ to a local directory, and run it using `make`.
One the SNMP MIBs have been downloaded to the local mibs/ directory, generate the snmp config with `snmp_generator generate`.
This will output a generated snmp.yml file. Copy this file to /etc/snmp_exporter/snmp.yml.

Note that additional MIBs can be added to the local mibs/ directory prior to running the `snmp_generator` command.
