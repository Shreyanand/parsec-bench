It is 2026-12-03 10:52 UTC. At 06:40 UTC on 2026-12-02 we moved `sftp-edge-cph-04` onto the new DMZ
VLAN, and its address is now 10.44.30.23. Icinga has shown that host as DOWN ever since, yet partner
uploads are still landing on it and I can SSH in. I'm about to raise a P1 with the network team.
Before I do, tell me what address and check Icinga is actually using for that host, at what UTC time
it went DOWN, how many hours it has been DOWN for, and whether this is a real outage.
