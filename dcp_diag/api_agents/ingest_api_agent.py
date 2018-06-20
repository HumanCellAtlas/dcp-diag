import requests

from .ingest_auth_agent import IngestAuthAgent


class IngestApiAgent:

    def __init__(self, deployment):
        self.deployment = deployment
        self.ingest_api_url = self._ingest_api_url()
        self.auth_headers = IngestAuthAgent().make_auth_header()

    def project(self, project_id):
        return IngestApiAgent.Project(project_id=project_id, ingest_api_agent=self)

    def submission(self, submission_id):
        return IngestApiAgent.SubmissionEnvelope(envelope_id=submission_id, ingest_api_agent=self)

    def iter_submissions(self):
        for page in self.iter_pages('/submissionEnvelopes', page_size=500):
            for submission_data in page['submissionEnvelopes']:
                yield IngestApiAgent.SubmissionEnvelope(data=submission_data, ingest_api_agent=self)

    """
    Get a collection resource.
    Iterates through all pages gathering results and returns a list.
    """
    def get_all(self, path_or_url, result_element_we_are_interested_in):
        results = []
        for page in self.iter_pages(path_or_url):
            results += page[result_element_we_are_interested_in]
        return results

    """
    Iterate through a collection using HATEOAS pagination, yielding pages.
    """
    def iter_pages(self, path_or_url, page_size=100):
        path_or_url += f"?size={page_size}"

        while True:
            data = self.get(path_or_url)
            if '_embedded' not in data:
                break

            yield data['_embedded']

            if 'next' in data['_links']:
                path_or_url = data['_links']['next']['href']
            else:
                break

    """
    Get a singleton resource.
    """
    def get(self, path_or_url):
        if path_or_url.startswith('http'):
            url = path_or_url
        else:
            url = f"{self.ingest_api_url}{path_or_url}"

        response = requests.get(url, headers=self.auth_headers)

        if response.ok:
            return response.json()
        else:
            raise RuntimeError(f"GET {url} got {response}")

    def _ingest_api_url(self):
        if self.deployment == 'prod':
            return "http://api.ingest.data.humancellatlas.org"
        else:
            return f"http://api.ingest.{self.deployment}.data.humancellatlas.org"

    class Project:

        def __init__(self, project_id, ingest_api_agent):
            self.project_id = project_id
            self.api = ingest_api_agent
            self.data = None
            self._load()

        @property
        def uuid(self):
            return self.data['uuid']

        def submission_envelopes(self):
            data = self.api.get(self.data['_links']['submissionEnvelopes']['href'])
            return [
                IngestApiAgent.SubmissionEnvelope(data=subm_data, ingest_api_agent=self.api)
                for subm_data in data['_embedded']['submissionEnvelopes']
            ]

        def _load(self):
            self.data = self.api.get(f"/projects/{self.project_id}")

    class SubmissionEnvelope:

        # May be primed wih data, or of you supply an ID, we will go get the data

        def __init__(self, ingest_api_agent, envelope_id=None, data=None):
            if not envelope_id and not data:
                raise RuntimeError("either envelope_id or data must be provided")
            self.api = ingest_api_agent
            self.data = None
            if envelope_id:
                self.envelope_id = envelope_id
                self._load()
            else:
                self.data = data
                self.envelope_id = data['_links']['self']['href'].split('/')[-1]

        def __str__(self):
            return f"SubmissionEnvelope(id={self.envelope_id}, uuid={self.uuid}, status={self.status})"

        def files(self):
            return self.api.get_all(self.data['_links']['files']['href'], 'files')

        def iter_files(self):
            url = self.data['_links']['files']['href']
            for page in self.api.iter_pages(url):
                for file in page['files']:
                    yield file

        def reload(self):
            self._load()
            return self

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

        def _load(self):
            self.data = self.api.get(f"/submissionEnvelopes/{self.envelope_id}")
