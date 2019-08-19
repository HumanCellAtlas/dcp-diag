# Changes for v1.2.0 (2019-08-19)
Make AzulAgent handle 400 errors
Switch to dcplib's IngestApiAgent and ingest_entities
Fix file <-> validation relationship in entities

# Changes for v1.1.1 (2019-05-15)
analyze-submission: update elasticsearch primary bundle search

# Changes for v1.1.0 (2019-05-15)
analyze-submission:
 - count extra bundles returned by a project UUID search in DSS
 - sort bundle lists when printing
 - save state after every phase
 - save state on Ctrl-C

# Changes for v1.0.1 (2019-04-02)
Fix Ingest authentication error


# Changes for v1.0.0 (2019-02-06)
Dcpdig can show batch jobs and their logs: dcpdig @upload validation_id=<uuid> --show batch_jobs,logs
Dcpdig can show workflows: dcpdig @analysis bundle_uuid=<uuid> --show bundles,projects
Use Ingest's HTTPS API endpoints.
Compatible with Upload database v4.1.0.


# Changes for v0.11.0 (2018-11-30)
dcpdig: Allow project_uuid=<x> --show submissions AND bundles

# Changes for v0.10.0 (2018-10-26)
dcpdig: allow 'all' as an option for --show

# Changes for v0.9.0 (2018-10-26)
dcpdig @upload [area|file_id]

# Changes for v0.8.0 (2018-10-24)
analyze-submission: show accurate starting counts when we already have partial results
Save all Ingest state in savefile, version the statefile schema.

# Changes for v0.7.0 (2018-10-24)
Use bundle FQID instead of UUID everywhere we can

# Changes for v0.6.2 (2018-10-23)
Now works in production environment too.

# Changes for v0.6.1 (2018-10-22)
Fix load vs clean bug

# Changes for v0.6.0 (2018-10-21)
analyze-submission:
 - use --jobs to configure concurrency
 - saves and reloads state automatically, use --clean to disable load
 - verbosity: -v = bad news detail, -vv = good and bad news detail

# Changes for v0.5.0 (2018-10-19)
scripts/dcpdig -d staging @ingest project_uuid=<uuid> --show submissions
scripts/analyze-submission -d <deployment> <submission_id>
  - checks bundle manifests are in AWS/GCP DSS
  - searches DSS AWS & GCP for bundles by project_id

# Changes for v0.4.0 (2018-09-14)
Refactor to make more extensible
gitignore build and dist dirs
fix error when no --show is supplied

# Changes for v0.3.0 (2018-09-12)
UX cleanup, add search for submission uuid
Add dcpdig usage notes to README

# Changes for v0.2.0 (2018-06-20)
dcpdig @ingest bundle_uuid=x

# Changes for v0.1.0 (2018-06-20)
dcpdig @ingest subm_uuid=x

