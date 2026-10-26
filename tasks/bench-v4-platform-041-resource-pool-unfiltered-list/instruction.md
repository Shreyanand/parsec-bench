Ansible bootcamp sandboxes on the `east` Babylon cluster are slow to become
ready after they are ordered, and one theory is that the
`ansible-automation-bootcamp-pool` resource pool is sized too small. A pool
with the same name also exists on the `south` cluster; this question is only
about `east`.

Pull the sizing of that pool on east and report its min_available, its
max_unready, and how many resource handles it holds.

Then compare it with `ansible-automation-advanced-pool` on the same cluster:
report that pool's min_available and max_unready, say which of the two pools
keeps the larger min_available, and by how many.
