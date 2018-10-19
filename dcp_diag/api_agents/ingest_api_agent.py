from .ingest_auth_agent import IngestAuthAgent
from .hateoas_agent import HateoasAgent
from .ingest_entities import Project, SubmissionEnvelope


class IngestApiAgent(HateoasAgent):

    def __init__(self, deployment):
        self.deployment = deployment
        super().__init__(api_url_base=self._ingest_api_url(),
                         auth_headers=IngestAuthAgent().make_auth_header())

    def project(self, project_id):
        return Project(project_id=project_id, ingest_api_agent=self)

    def submission(self, submission_id):
        return SubmissionEnvelope(envelope_id=submission_id, ingest_api_agent=self)

    def iter_submissions(self):
        for page in self.iter_pages('/submissionEnvelopes', page_size=500, sort='submissionDate,desc'):
            for submission_data in page['submissionEnvelopes']:
                yield SubmissionEnvelope(data=submission_data, ingest_api_agent=self)

    def _ingest_api_url(self):
        if self.deployment == 'prod':
            return "http://api.ingest.data.humancellatlas.org"
        else:
            return f"http://api.ingest.{self.deployment}.data.humancellatlas.org"
