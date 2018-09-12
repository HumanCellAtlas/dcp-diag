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

Usage: `dpdig @<component> <expression> --show <entities_to_show>`

Examples:

Find the submission relating to a DSS bundle UUID:

    dcpdig @ingest bundle_uuid=<x>

Find a (Mongo) submission ID given a submission UUID:

    dcpdig @ingest submission_uuid=<x>

Note that submission may be abbreviated to "subm" or "sub", e.g.
`subm_uuid=x`.

Show files and bundles associated with an Ingest submission with Mongo ID `foo`:

    `dcpdig @ingest subm_id=foo --show files,bundles`


