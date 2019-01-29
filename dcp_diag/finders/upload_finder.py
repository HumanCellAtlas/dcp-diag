from sqlalchemy.orm.exc import NoResultFound

from .. import DcpDiagException
from .finder import Finder

from dcp_diag.component_entities.upload_entities import DbUploadArea, DbFile, DbValidation, BatchJob, DBSessionMaker


class UploadFinder:

    """
    dcpdig @upload area=<uuid>
    dcpdig @upload file_id=<upload-area>/<filename>
    """

    name = 'upload'

    def __init__(self, deployment, **args):
        self.deployment = deployment

    def find(self, expression):
        field_name, field_value = expression.split('=')
        db = DBSessionMaker(self.deployment).session()

        if field_name == 'file':
            try:
                file = db.query(DbFile).filter(DbFile.s3_key == field_value).one()
                return file
            except NoResultFound:
                raise DcpDiagException(f"No record of File \"{field_value}\""
                                       f" found in Upload's {self.deployment} database.")

        elif field_name == 'area_id' or field_name == 'area':
            try:
                area = db.query(DbUploadArea).filter(DbUploadArea.uuid == field_value).one()
                return area
            except NoResultFound:
                raise DcpDiagException(f"No record of Upload Area \"{field_value}\""
                                       f" found in Upload's {self.deployment} database.")

        elif field_name == 'validation_id' or field_name == 'validation':
            try:
                validation = db.query(DbValidation).filter(DbValidation.id == field_value).one()
                return validation
            except NoResultFound:
                raise DcpDiagException(f"No record of Validation \"{field_value}\""
                                       f" found in Upload's {self.deployment} database.")

        elif field_name == 'batch_job' or field_name == 'job_id':
            return BatchJob.find_by_id(field_value)

        else:
            raise DcpDiagException(f"Sorry I don't know how to find an {field_name}")


Finder.register(UploadFinder)
