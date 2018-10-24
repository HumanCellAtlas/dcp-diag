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

