import re
import sys

from ..api_agents import IngestApiAgent


class IngestFinder:

    def __init__(self, deployment):
        self.ingest = IngestApiAgent(deployment=deployment)

    def find(self, expression, display_this=None):

        field_name, field_value = expression.split('=')

        # substitute 'sub', 'subm' -> 'submission'
        field_name = re.sub(r"sub([^a-z])", "submission\\1", field_name)
        field_name = re.sub(r"subm([^a-z])", "submission\\1", field_name)

        if field_name == 'submission_uuid':
            return self.find_submission_uuid(subm_uuid=field_value)
        elif field_name == 'bundle_uuid':
            return self.find_bundle_uuid(bundle_uuid=field_value)
        else:
            print(f"Sorry I don't know how to find a {field_name}")
            exit(1)

    def find_submission_uuid(self, subm_uuid):
        print(f"Searching for submission with UUID {subm_uuid}...")
        count = 0
        for subm in self.ingest.iter_submissions():
            count += 1
            sys.stdout.write(f"\rSearched {count} submissions...")
            sys.stdout.flush()

            if subm.uuid == subm_uuid:
                print(f"\nSubmission {subm.envelope_id} has UUID {subm_uuid}")
                break

    def find_bundle_uuid(self, bundle_uuid):
        print(f"Searching for submission with Bundle {bundle_uuid}...")
        count = 0
        for subm in self.ingest.iter_submissions():
            count += 1
            sys.stdout.write(f"\rSearched {count} submissions...")
            sys.stdout.flush()

            for subm_bundle_uuid in subm.bundles():
                if subm_bundle_uuid == bundle_uuid:
                    print(f"\nBundle {bundle_uuid} is in the manifest for submission {subm.envelope_id}")
                    exit(0)
