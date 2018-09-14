from urllib.parse import urlencode

import requests

from .ingest_auth_agent import IngestAuthAgent
from .ingest_entities import Project, SubmissionEnvelope


class IngestApiAgent:

    def __init__(self, deployment):
        self.deployment = deployment
        self.ingest_api_url = self._ingest_api_url()
        self.auth_headers = IngestAuthAgent().make_auth_header()

    def project(self, project_id):
        return Project(project_id=project_id, ingest_api_agent=self)

    def submission(self, submission_id):
        return SubmissionEnvelope(envelope_id=submission_id, ingest_api_agent=self)

    def iter_submissions(self):
        for page in self.iter_pages('/submissionEnvelopes', page_size=500, sort='submissionDate,desc'):
            for submission_data in page['submissionEnvelopes']:
                yield SubmissionEnvelope(data=submission_data, ingest_api_agent=self)

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
    def iter_pages(self, path_or_url, page_size=100, sort=None):
        url_params = {'size': page_size}
        if sort:
            url_params['sort'] = sort
        path_or_url += '?' + urlencode(url_params)

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
