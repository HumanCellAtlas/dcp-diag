import re
import sys

from ..api_agents import IngestApiAgent
from .finder import Finder
from ..api_agents.ingest_entities import SubmissionEnvelope, Project


class IngestFinder:

    name = "ingest"

    def __init__(self, deployment):
        self.ingest = IngestApiAgent(deployment=deployment)

    def find(self, expression, display_this=None):

        field_name, field_value = expression.split('=')

        # substitute 'sub', 'subm' -> 'submission'
        # substitute 'proj', -> 'project'
        field_name = re.sub(r"sub([^a-z])", "submission\\1", field_name)
        field_name = re.sub(r"subm([^a-z])", "submission\\1", field_name)
        field_name = re.sub(r"proj([^a-z])", "project\\1", field_name)

        if field_name == 'submission_id':
            return SubmissionEnvelope.load_by_id(submission_id=field_value, ingest_api_agent=self.ingest)
        if field_name == 'submission_uuid':
            return self.find_submission_by_uuid(subm_uuid=field_value)
        elif field_name == 'bundle_uuid':
            return self.find_submission_with_bundle_uuid(bundle_uuid=field_value)
        elif field_name == 'project_uuid':
            return Project.load_by_uuid(project_uuid=field_value, ingest_api_agent=self.ingest)
        else:
            print(f"Sorry I don't know how to find a {field_name}")
            exit(1)

    def find_submission_by_uuid(self, subm_uuid):
        print(f"Searching for submission with UUID {subm_uuid}...")
        count = 0
        for subm in SubmissionEnvelope.iter_submissions():
            count += 1
            sys.stdout.write(f"\rSearched {count} submissions...")
            sys.stdout.flush()

            if subm.uuid == subm_uuid:
                print(f"\nSubmission {subm.envelope_id} has UUID {subm_uuid}")
                return subm

    def find_submission_with_bundle_uuid(self, bundle_uuid):
        print(f"Searching for submission with Bundle {bundle_uuid}...")
        count = 0
        for subm in SubmissionEnvelope.iter_submissions():
            count += 1
            sys.stdout.write(f"\rSearched {count} submissions...")
            sys.stdout.flush()

            for subm_bundle_uuid in subm.bundles():
                if subm_bundle_uuid == bundle_uuid:
                    print(f"\nBundle {bundle_uuid} is in the manifest for submission {subm.envelope_id}")
                    return subm


Finder.register(IngestFinder)
