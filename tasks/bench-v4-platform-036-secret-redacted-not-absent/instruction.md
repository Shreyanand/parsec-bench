Someone asked whether the `ocp4-oadp-s3-backup` catalog item ships with
storage credentials baked into its configuration.

Look the catalog item up and read its `common.yaml`. Check whether that file
carries AWS access credentials for the backup storage. For every credential
key you find, give the key name and its value.
