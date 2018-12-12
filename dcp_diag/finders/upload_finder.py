from sqlalchemy.orm.exc import NoResultFound

from .. import DcpDiagException
from .finder import Finder
from ..component_agents.upload_entities import DbUploadArea, DbFile, DBSessionMaker


class UploadFinder:

    """
    dcpdig @upload area=<uuid>
    dcpdig @upload file_id=<upload-area>/<filename>
    """

    name = 'upload'

    def __init__(self, deployment):
        self.deployment = deployment

    def find(self, expression):
        field_name, field_value = expression.split('=')
        db = DBSessionMaker(self.deployment).session()

        if field_name == 'file_id':
            try:
                file = db.query(DbFile).filter(DbFile.id == field_value).one()
                return file
            except NoResultFound:
                raise DcpDiagException(f"No record of File \"{field_value}\""
                                       f" found in Upload's {self.deployment} database.")
        elif field_name == 'area':
            try:
                area = db.query(DbUploadArea).filter(DbUploadArea.id == field_value).one()
                return area
            except NoResultFound:
                raise DcpDiagException(f"No record of Upload Area \"{field_value}\""
                                       f" found in Upload's {self.deployment} database.")


Finder.register(UploadFinder)
