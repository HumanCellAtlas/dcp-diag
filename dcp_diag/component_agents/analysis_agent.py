from cromwell_tools import api as cwm_api
from cromwell_tools import cromwell_auth as cwm_auth


class AnalysisAgent:
    def __init__(self, deployment):
        """

        Args:
            deployment:
        """
        self.deployment = deployment
