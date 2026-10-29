Storage on-call here. On 2026-12-04 at 15:00 UTC we swapped the SFP and the patch cable on
ens2f1 of `ceph-osd-yul-14`, because Icinga was flagging CRC errors on it. It is 2026-12-09 at 10:00 UTC and the NIC
error check on that host is still CRITICAL, and I'm about to open another hardware ticket.
Before I do: what exactly does that check measure, what value and threshold is it alerting
on, are the CRC errors still happening, and what would it take for the check to go back to
OK? The plugin lives in `rhpds/rhdp-monitoring`; its path is in the service's vars.
