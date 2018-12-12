Data Coordination Platform Diagnostic Library and Tools
=======================================================

This repository and Python package contains diagnostic tools and a
library of code useful in building them.

## Installation

    pip install dcp-diag

## Dcpdig

`dcpdig` is a CLI tool to allow to interrogate DCP APIs and
that embodies knowledge of the links between entities in the
DCP to allow it to walk the object graph.

### Usage

Usage: `dcpdig --deployment=<deployment> @<component> <expression> --show <entities_to_show>`

#### Usage with the Ingestion Service

Use component `@ingest`.

Expressions:

```
submission_id=<mongo-id>
submission_uuid=<uuid>
project_uuid=<uuid>
bundle_uuid=<uuid>
```

Abbreviations that may be used in expressions:

* `summission` may be abbreviated to `subm`, e.g. `subm_uuid`.
* `project` may be abbreviated to `proj`.

Entities:

```
submissions
bundles
files
```

Examples:

Given a project UUID from the integration environment, show submissions
and their bundles and files:

    dcpdig -d integration @ingest proj_uuid=<uuid> --show all

Find a (Mongo) submission ID given a submission UUID:

    dcpdig -d staging @ingest submission_uuid=<x>

Show bundles associated with an Ingest submission with Mongo ID `foo`:

    dcpdig -d dev @ingest subm_id=foo --show bundles

Find the submission relating to a DSS bundle UUID.  This does a "brute
force" search through all submissions to find the one using this bundle:

    dcpdig -d dev @ingest bundle_uuid=<x>

#### Usage with the Upload Service

Use component `@upload`.

Expressions:

```
area=<uuid>
file_id=<uuid>/<filename>
validation_id=<uuid>
batch_job=<uuid>
```

Entities:

```
files
checksums
validations
notifications
batch_jobs
logs
```
or use `all`

Permisions: you must be using AWS credentials (typically an AWS_PROFILE)
that has access to the Upload Service secrets in AWS SecretsManager.
Most DCP developers has this level of access.

Examples:

Exhaustively dump everything associated with an upload area, verbosely.
This can be very long:

    dcpdig @upload area=<uuid> --show all -v

Show file, checksum records for a single file:

    dcpdig @upload file_id=<uuid>/<filename> --show checksums

Show validation, batch job records and job log:

    dcpdig @upload validation_id=<uuid> --show batch_jobs,logs
