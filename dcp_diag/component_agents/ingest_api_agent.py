from .ingest_auth_agent import IngestAuthAgent
from .hateoas_agent import HateoasAgent


class IngestApiAgent(HateoasAgent):

    def __init__(self, deployment):
        self.deployment = deployment
        super().__init__(api_url_base=self._ingest_api_url(),
                         auth_headers=IngestAuthAgent().make_auth_header())

    def _ingest_api_url(self):
        if self.deployment == 'prod':
            return "http://api.ingest.data.humancellatlas.org"
        else:
            return f"http://api.ingest.{self.deployment}.data.humancellatlas.org"
