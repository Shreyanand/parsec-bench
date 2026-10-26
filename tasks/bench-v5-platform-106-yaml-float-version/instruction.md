We are rehearsing the summit service mesh lab on the evening of 2026-10-05, and its provision just died downloading the OpenShift installer. The run is job 915738 on the `event0` controller. The lab is meant to install OpenShift 4.20.

I think the artifact server we pull installers from is flaking. If that's what it is, relaunch the job for me. If it isn't, tell me what the download actually requested and why. The lab's settings live in its agnosticv catalog item, so look that up and read its configuration. Tell me what to change, and finish with a root-cause category and your confidence.
