import json

from termcolor import colored

from . import EntityBase


class Project(EntityBase):
    """
    Model an Ingest Project entity
    """

    @classmethod
    def load_by_id(cls, project_id, ingest_api_agent):
        data = ingest_api_agent.get(f"/projects/{project_id}")
        return Project(project_data=data, ingest_api_agent=ingest_api_agent)

    @classmethod
    def load_by_uuid(cls, project_uuid, ingest_api_agent):
        data = ingest_api_agent.get(f"/projects/search/findByUuid?uuid={project_uuid}")
        return Project(project_data=data, ingest_api_agent=ingest_api_agent)

    def __init__(self, project_data=None, ingest_api_agent=None):
        self.api = ingest_api_agent
        self.data = project_data

    def __str__(self, prefix="", verbose=False):
        return colored(f"{prefix}Project {self.id}\n", 'green') + \
               f"{prefix}    uuid={self.uuid}\n" \
               f"{prefix}    short_name={self.short_name}\n"

    @property
    def id(self):
        return self.data['_links']['self']['href'].split('/')[-1]

    @property
    def uuid(self):
        return self.data['uuid']['uuid']

    @property
    def short_name(self):
        return self.data['content']['project_core']['project_short_name']

    def print(self, prefix="", verbose=False, associated_entities_to_show=None):
        print(self.__str__(prefix=prefix, verbose=verbose))
        if associated_entities_to_show:
            prefix = f"{prefix}\t"
            if 'submissions' in associated_entities_to_show or 'all' in associated_entities_to_show:
                for subm in self.submission_envelopes():
                    subm.print(prefix=prefix, verbose=verbose, associated_entities_to_show=associated_entities_to_show)

    def submission_envelopes(self):
        data = self.api.get(self.data['_links']['submissionEnvelopes']['href'])
        return [
            SubmissionEnvelope(submission_data=subm_data, ingest_api_agent=self.api)
            for subm_data in data['_embedded']['submissionEnvelopes']
        ]


class SubmissionEnvelope(EntityBase):
    """
    Model an Ingest Submission Envelope entity
    """

    @classmethod
    def load_by_id(cls, submission_id, ingest_api_agent):
        data = ingest_api_agent.get(f"/submissionEnvelopes/{submission_id}")
        return SubmissionEnvelope(submission_data=data, ingest_api_agent=ingest_api_agent)

    @classmethod
    def iter_submissions(cls, ingest_api_agent):
        for page in ingest_api_agent.iter_pages('/submissionEnvelopes', page_size=500, sort='submissionDate,desc'):
            for submission_data in page['submissionEnvelopes']:
                yield SubmissionEnvelope(submission_data=submission_data, ingest_api_agent=ingest_api_agent)

    def __init__(self, submission_data, ingest_api_agent):
        self.data = submission_data
        self.api = ingest_api_agent
        self.envelope_id = self.data['_links']['self']['href'].split('/')[-1]

    def __str__(self, prefix="", verbose=False):
        return colored(f"{prefix}SubmissionEnvelope {self.envelope_id}\n", 'green') + \
               f"{prefix}    uuid={self.uuid}\n" \
               f"{prefix}    status={self.status}"

    def print(self, prefix="", verbose=False, associated_entities_to_show=None):
        print(self.__str__(prefix=prefix, verbose=verbose))
        if associated_entities_to_show:
            prefix = f"{prefix}    "
            if 'bundles' in associated_entities_to_show or 'all' in associated_entities_to_show:
                if self.status == 'Complete':
                    print(colored(f"{prefix}Bundles:", 'cyan'))
                    for bundle in self.bundles():
                        print(prefix + "    " + bundle)

            if 'files' in associated_entities_to_show or 'all' in associated_entities_to_show:
                    print(colored(f"{prefix}Files:", 'cyan'))
                    for file in self.files():
                        file.print(prefix=prefix, verbose=verbose,
                                   associated_entities_to_show=associated_entities_to_show)

    def files(self):
        return [File(file_data) for file_data in
                self.api.get_all(self.data['_links']['files']['href'], 'files')]

    def iter_files(self):
        url = self.data['_links']['files']['href']
        for page in self.api.iter_pages(url):
            for file in page['files']:
                yield file

    def projects(self):
        return [Project(project_data=proj_data, ingest_api_agent=self.api) for proj_data in
                self.api.get_all(self.data['_links']['projects']['href'], 'projects')]

    def project(self):
        """ Assumes only one project """
        projects = self.projects()
        if len(projects) != 1:
            raise RuntimeError(f"Expect 1 project got {len(projects)}")
        return projects[0]

    @property
    def status(self):
        return self.data['submissionState']

    @property
    def uuid(self):
        return self.data['uuid']['uuid']

    def upload_credentials(self):
        """ Return upload area credentials or None if this envelope doesn't have an upload area yet """
        staging_details = self.data.get('stagingDetails', None)
        if staging_details and 'stagingAreaLocation' in staging_details:
            return staging_details.get('stagingAreaLocation', {}).get('value', None)
        return None

    def bundles(self):
        url = self.data['_links']['bundleManifests']['href']
        manifests = self.api.get_all(url, 'bundleManifests')
        return [manifest['bundleUuid'] for manifest in manifests]


class File:
    """
    Model an Ingest File entity
    """

    def __init__(self, file_data):
        self._data = file_data

    def __str__(self, prefix="", verbose=False):
        return (f"{prefix}    fileName {self.name}\n" +
                f"{prefix}    cloudUrl {self.cloud_url}\n")

    def __repr__(self):
        return json.dumps(self._data, indent=2)

    @property
    def name(self):
        return self._data['fileName']

    @property
    def cloud_url(self):
        return self._data['cloudUrl']

    def print(self, prefix="", verbose=False, associated_entities_to_show=None):
        print(self.__str__(prefix=prefix, verbose=verbose))
