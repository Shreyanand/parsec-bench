The Dev Spaces Workshop provisioned cleanly on 2026-10-02 (AAP2 job `5528440`, which
ran agnosticd at revision `e41d07a9b2c6`). The next morning job `5530918` on
controller `east` failed while installing the Dev Spaces operator. A teammate is sure
somebody pushed a breaking change to agnosticd on the night of 2026-10-02 and wants to start bisecting
commits.

Before anyone bisects, tell me what broke and why it happened, and whether anything
changed in agnosticd between the two runs. The job log says which runtime the job used;
follow that to its build definition.
