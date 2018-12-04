from .. import DcpDiagException
from .finder import Finder


class AnalysisFinder:

    """
    dcpdig @analysis workflow_uuid=<id>
    dcpdig @analysis project_uuid=<id>
    dcpdig @analysis bundle_uuid=<id>
    """

    name = 'analysis'

    def __init__(self, deployment):
        self.deployment = deployment

    def find(self, expression):
        """

        Args:
            expression:
        """
        field_name, field_value = expression.split('=')

        if field_name == 'workflow_uuid':
            print("Searching for the workflow(s) associated with the workflow_uuid for you!")

        elif field_name == 'project_uuid':
            print("Searching for the workflow(s) associated with the project_uuid for you!")

        elif field_name == 'bundle_uuid':
            print("Searching for the workflow(s) associated with the primary bundle_uuid for you!")

        else:
            print(f"Sorry I don't know how to find a {field_name}")
            exit(1)


Finder.register(AnalysisFinder)
