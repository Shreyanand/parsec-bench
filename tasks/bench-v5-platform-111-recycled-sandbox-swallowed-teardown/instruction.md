Our Service Mesh Tracing Lab order died on controller `east` in AAP2 job `3304817`
with `VpcLimitExceeded`. The lab only builds one VPC, so I don't understand how it hit
a VPC limit, and my first instinct is to file an AWS quota increase for the pool.

Before I do that: explain why this provision failed. The sandbox account it ran in had
been used before, so find the job that last cleaned that account, check what that
cleanup actually did and how many of the account's VPCs it left behind, and name the
setting responsible.
