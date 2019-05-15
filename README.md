Data Coordination Platform Diagnostic Library and Tools
=======================================================
![Github](https://img.shields.io/badge/python-3.6-green.svg?style=for-the-badge&logo=python)
![GitHub](https://img.shields.io/github/license/HumanCellAtlas/dcp-diag.svg?style=for-the-badge)
[![GitHub release](https://img.shields.io/github/tag/HumanCellAtlas/dcp-diag.svg?label=Latest%20Release&style=for-the-badge&colorB=green)](https://github.com/HumanCellAtlas/dcp-diag/releases)

This repository and Python package contains diagnostic tools and a
library of code useful in building them.

## Installation

    pip install dcp-diag

## Analyze-submission

`analyze-submission` is a tool to allow data wrangers to examine the
progress of a submission through the DCP.  Please don't use it unless
you're a data wranger - it can be very API-call intensive.

It will check the submission envelope, primary and secondary bundle
manifests in the DSS, project search results in the DSS, Secondary
Analysis workflows (if you have credentials to allow that) and Azul
search results.

### Usage

```
analyze-submission --deployment="<deployment>" <submission-id>
```

* The default level of output is a summary only.
* Adding `--verbose` or `-v` will show UUIDs of problem entities (bundles/workflows).
* Adding a second level `-vv` will show UUIDs of all entities found.

`analyze-submission` caches results in a (human readable)
`<submission-id>.json` file, and is restartable.  It is built this way
as it can take a long time to run for large submissions, and as such can
be victim to network and API faulures.
If you wish to clear the cache for a particular
submission and get all fresh data, add option `--fresh`.

### Example Output

```
analyze-submission -d prod 1234567890abcdef12345678 --credentials=creds.json

Using deployment: prod

PHASE 1: Get submission primary bundle list from Ingest:
	Submission ID: 1234567890abcdef12345678
	Project UUID: 11111111-2222-3333-4444-555555555555
	Ingest created 6 bundles.

PHASE 2: Checking bundles are present in DSS:
	6 bundle are present in AWS
	6 bundle are present in GCP

PHASE 3: Check DSS for primary bundles with this project UUID:
	In AWS DSS, 6 primary bundles are indexed by project
	In GCP DSS, 6 primary bundles are indexed by project

PHASE 4: Check Secondary Analysis for workflows with this project UUID:
	Workflows are succeeded  : 6/6
	Workflows are in progress: 0/6
	Workflows are failed     : 0/6

PHASE 5: Check DSS for secondary bundles:
	In AWS there are 6 primary bundles with 1 results bundles
	In GCP there are 6 primary bundles with 1 results bundles

PHASE 6: Check Azul for primary bundles:
	In Azul, 6 primary bundles are indexed

PHASE 7: Check Azul for secondary bundles:
	In Azul there are 6 primary bundles with 1 results bundles
```

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
file=<uuid>/<filename>
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

**Permisions**: you must be using AWS credentials (typically an AWS_PROFILE)
that has access to the Upload Service secrets in AWS SecretsManager.
Most DCP developers has this level of access.

Examples:

Exhaustively dump everything associated with an upload area, verbosely.
This can be very long:

    dcpdig @upload area=<uuid> --show all -v

Show file, checksum records for a single file:

    dcpdig @upload file=<uuid>/<filename> --show checksums

Show validation, batch job records and job log:

    dcpdig @upload validation_id=<uuid> --show batch_jobs,logs

#### Usage with the Data Processing Pipeline Service

Use component `@analysis`.

Expressions:

```
wf_uuid=<uuid>
workflow_uuid=<uuid>
bundle_uuid=<uuid>
```

Entities:

```
bundle/bundles
project/projects
```
or use `all`

**Permisions**: you must provide the path to the GCP service account JSON key
that has access to the Data Processing Pipeline Service's workflow execution engines, otherwise the analysis commands will return `No auth information provided, skip checking Secondary Analysis for workflows.` to you.

Examples:

Given a analysis workflow UUID from the integration environment, show associated primary bundle(s) and project(s), in a compact style:

```bash
dcpdig @analysis workflow_uuid=<uuid> -d integration --credentials=<path/to/gcp/service/account/key.json> --show bundles,projects
```

Given a analysis workflow UUID from the integration environment, show associated primary bundle(s) and project(s), in a verbose style:

```bash
dcpdig @analysis workflow_uuid=<uuid> -d integration --credentials=<path/to/gcp/service/account/key.json> -v -s all
```

Given a primary bundle UUID from the integration environment, show all of the workflows it triggered, with each workflow's associated primary bundle(s) and project(s), in a compact style:

```bash
dcpdig @analysis bundle_uuid=<uuid> -d integration --credentials=<path/to/gcp/service/account/key.json> --show bundles,projects
```

Given a primary bundle UUID from the integration environment, show all of the workflows it triggered, with each workflow's associated primary bundle(s) and project(s), in a verbose style:

```bash
dcpdig @analysis bundle_uuid=<uuid> -d integration --credentials=<path/to/gcp/service/account/key.json> -v -s all
```

## Contributing
