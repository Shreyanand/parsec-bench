Our OpenShift GitOps Day on the Babylon cluster `skua` ended on 2026-11-18. Each attendee
ordered the event lab into their own namespace, and I need to delete whatever is left
before the next run. The eight attendee namespaces are:

- `user-lmoreau-redhat-com`
- `user-kdasgupta-redhat-com`
- `user-pferreira-redhat-com`
- `user-jnakashima-redhat-com`
- `user-ebrennan-redhat-com`
- `user-sokoye-redhat-com`
- `user-mlindgren-redhat-com`
- `user-hcastillo-redhat-com`

For each namespace, list every ResourceClaim from the event's catalog item that still
exists, with its GUID, whatever state it is in. Leave out labs people ordered for
themselves from other items. Then tell me how many leftover event claims there are in
total and how many attendees still hold one.
