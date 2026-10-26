The `ldap-bind` check on Icinga host `sso-broker-vie-2` has been UNKNOWN since 07:12 UTC on
2026-12-10, and a colleague wants to page the IdM on-call because "LDAP is timing out". The
IdM team swears the directory is fine. The plugin is in `rhpds/rhdp-monitoring` at the path in
the service vars. Work out why the check is UNKNOWN and whether LDAP is really down, check the
directory servers the check is configured to use, and tell me what has to change for the
check to work again. Also: if one of those servers is dead, why did nobody get paged about it?
Don't acknowledge or re-run anything in Icinga; I just want the explanation.
