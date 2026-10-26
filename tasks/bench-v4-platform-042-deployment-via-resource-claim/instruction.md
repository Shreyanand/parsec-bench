A user reports that their Babylon lab with GUID `tq4hm` on the `west`
cluster seems to be stuck.

Find the AnarchySubject for that GUID on `west`, then check the Babylon
deployment (the ResourceClaim) that actually backs that subject.

For that deployment, tell me whether it is healthy, whether it is ready,
which catalog item it was ordered from, and the asset UUID it carries.
