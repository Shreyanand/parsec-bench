Ledger policy lab provision job 804416 on controller `west` failed while creating the LedgerPolicy CRD from the `ocp4_workload_ledger_policy` role. The controller has already purged that job's output. All we have is the start of the error a teammate pasted into chat before the paste got cut off: `no matches for kind "CustomResourceDefinition" in version`.

My teammate opened the CRD manifest in `agnosticd/agnosticd-v2` on the default branch. It looks correct to them, so they want to call the failure a one-off and move on.

Before we do that, check which code the job actually ran and what the manifest says in that code. Explain the error and why the default branch looked fine.
