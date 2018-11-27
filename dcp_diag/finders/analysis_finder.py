from .. import DcpDiagException
from .finder import Finder


class AnalysisFinder:

    """
    dcpdig @analysis workflow=<id>
    dcpdig @analysis project=<id>
    """

    name = 'analysis'

    def __init__(self, deployment):
        self.deployment = deployment

    def find(self, expression):
        field_name, field_value = expression.split('=')

        if field_name == 'workflow':
            print("SAM: workflow!")

        elif field_name == 'project':
            pass


Finder.register(AnalysisFinder)
