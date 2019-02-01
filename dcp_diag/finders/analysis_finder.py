from .. import DcpDiagException
from .finder import Finder

from dcp_diag.component_agents.analysis_agent import AnalysisAgent
import re


class AnalysisFinder:

    """
    dcpdig @analysis workflow_uuid=<id>
    dcpdig @analysis bundle_uuid=<id>
    """

    name = 'analysis'

    def __init__(self, deployment, **args):
        self.deployment = deployment
        # FIXME: Use a better way to authenticate instead of asking for service account JSON key
        # FIXME: If use OAuth, this should align with the Ingest Agent
        self.service_account_key = args.get('credentials')
        with AnalysisAgent.ignore_logging_msg():
            self.analysis = AnalysisAgent(deployment=self.deployment, service_account_key=self.service_account_key)

    def find(self, expression):
        """Find the target entities based on the expression.

        Args:
            expression (str): An expression representing the targeting entity with it value, separated by '='.
                It also supports shorthands, e.g.
                - "bundle_uuid='xxx'"
                - "workflow_uuid='yyy'"
                - "wf_uuid='yyy'"
        """
        if not self.service_account_key:
            raise DcpDiagException("No auth information provided, skip checking Secondary Analysis for workflows.")

        field_name, field_value = expression.split('=')

        # substitute 'wf_id', -> 'workflow_id'
        field_name = re.sub(r"wf([^a-z])", "workflow\\1", field_name)

        if field_name == 'workflow_uuid':
            print(f"Searching for workflow with UUID {field_name}...")
            with self.analysis.ignore_logging_msg():
                return self.analysis.query_by_workflow_uuid(uuid=field_value)

        elif field_name == 'bundle_uuid':
            print(f"Searching for workflow(s) with Bundle {field_name}...")
            with self.analysis.ignore_logging_msg():
                candidates = self.analysis.query_by_bundle(bundle_uuid=field_value)
                return candidates

        else:
            print(f"Sorry I don't know how to find a {field_name}")
            exit(1)


Finder.register(AnalysisFinder)
