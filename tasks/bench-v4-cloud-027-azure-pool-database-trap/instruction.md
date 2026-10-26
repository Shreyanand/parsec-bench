Look up the Azure subscription `pool-01-389`.

It is in the standard Azure **pools** database -- not the ARO database and
not the roadshow one. `query_azure_pools` takes a `database` argument and
only accepts those three values, so pass the right one.

Report whether the subscription is assigned and, if it is, which RHDP
project tag it is assigned to. Then list the subscriptions in that database,
say how many there are in total, and name one that is free to hand out.
