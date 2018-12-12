from datetime import datetime

from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from termcolor import colored

from dcplib.config import Config

from . import EntityBase

DbBase = declarative_base(name='DbBase')


class UploadDbConfig(Config):
    def __init__(self, *args, **kwargs):
        super().__init__(component_name='upload', secret_name='database', **kwargs)


class DBSessionMaker:

    def __init__(self, deployment):
        engine = create_engine(UploadDbConfig(deployment=deployment).database_uri)
        DbBase.metadata.bind = engine
        self.session_maker = sessionmaker()
        self.session_maker.bind = engine

    def session(self):
        return self.session_maker()


class DbUploadArea(DbBase, EntityBase):
    __tablename__ = 'upload_area'
    id = Column(String(), primary_key=True)
    bucket_name = Column(String(), nullable=False)
    status = Column(String(), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False, onupdate=datetime.utcnow)

    def __str__(self, prefix="", verbose=False):
        return colored(f"{prefix}Upload Area {self.id}\n", 'blue') + \
            f"{prefix}    bucket_name: {self.bucket_name}\n" \
            f"{prefix}         Status: {self.status}\n" \
            f"{prefix}     created_at: {self.created_at}\n" \
            f"{prefix}     updated_at: {self.updated_at}\n"

    def print(self, prefix="", verbose=False, associated_entities_to_show=None):
        print(self.__str__(prefix=prefix, verbose=verbose))
        if associated_entities_to_show:
            if 'files' in associated_entities_to_show or 'all' in associated_entities_to_show:
                prefix = f"\t{prefix}"
                for file in self.files:
                    file.print(prefix=prefix, verbose=verbose, associated_entities_to_show=associated_entities_to_show)


class DbFile(DbBase, EntityBase):
    __tablename__ = 'file'
    id = Column(String(), primary_key=True)
    upload_area_id = Column(String(), ForeignKey('upload_area.id'), nullable=False)
    name = Column(String(), nullable=False)
    size = Column(Integer(), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False, onupdate=datetime.utcnow)

    upload_area = relationship("DbUploadArea", back_populates="files")

    def __str__(self, prefix="", verbose=False):
        return colored(f"{prefix}File {self.id}\n", 'green') + \
            f"{prefix}    Upload Area ID: {self.upload_area_id}\n" \
            f"{prefix}              Name: {self.name}\n" \
            f"{prefix}              Size: {self.size}\n" \
            f"{prefix}        created_at: {self.created_at}\n" \
            f"{prefix}        updated_at: {self.updated_at}\n"

    def print(self, prefix="", verbose=False, associated_entities_to_show=None):
        print(self.__str__(prefix=prefix, verbose=verbose))
        if associated_entities_to_show:
            prefix = f"\t{prefix}"
            if 'checksums' in associated_entities_to_show or 'all' in associated_entities_to_show:
                for checksum in self.checksums:
                    checksum.print(prefix=prefix, verbose=verbose,
                                   associated_entities_to_show=associated_entities_to_show)
            if 'validations' in associated_entities_to_show or 'all' in associated_entities_to_show:
                for val in self.validations:
                    val.print(prefix=prefix, verbose=verbose,
                              associated_entities_to_show=associated_entities_to_show)
            if 'notifications' in associated_entities_to_show or 'all' in associated_entities_to_show:
                for notif in self.notifications:
                    notif.print(prefix=prefix, verbose=verbose,
                                associated_entities_to_show=associated_entities_to_show)


class DbChecksum(DbBase, EntityBase):
    __tablename__ = 'checksum'
    id = Column(String(), primary_key=True)
    file_id = Column(String(), ForeignKey('file.id'), nullable=False)
    job_id = Column(String(), nullable=False)
    status = Column(String(), nullable=False)
    checksums = Column(String(), nullable=False)
    checksum_started_at = Column(DateTime(), nullable=False)
    checksum_ended_at = Column(DateTime(), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False, onupdate=datetime.utcnow)

    file = relationship("DbFile", back_populates='checksums')

    def __str__(self, prefix="", verbose=False):
        output = colored(f"{prefix}Checksum {self.id}\n", 'cyan') + \
                 f"{prefix}                File ID: {self.file_id}\n" \
                 f"{prefix}                 Job ID: {self.job_id}\n" \
                 f"{prefix}                 Status: {self.status}\n" \
                 f"{prefix}    checksum_started_at: {self.checksum_started_at}\n" \
                 f"{prefix}      checksum_ended_at: {self.checksum_ended_at}\n" \
                 f"{prefix}             created_at: {self.created_at}\n" \
                 f"{prefix}             updated_at: {self.updated_at}\n"
        if verbose:
            output = output + f"{prefix}              checksums: {self.checksums}\n"
        return output

    def print(self, prefix="", verbose=False, associated_entities_to_show=None):
        print(self.__str__(prefix=prefix, verbose=verbose))


class DbNotification(DbBase, EntityBase):
    __tablename__ = 'notification'
    id = Column(String(), primary_key=True)
    file_id = Column(String(), ForeignKey('file.id'), nullable=False)
    status = Column(String(), nullable=False)
    payload = Column(JSON(), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False, onupdate=datetime.utcnow)

    file = relationship("DbFile", back_populates='notifications')

    def __str__(self, prefix="", verbose=False):
        output = colored(f"{prefix}Notification {self.id}\n", 'magenta') + \
                 f"{prefix}       File ID: {self.file_id}\n" \
                 f"{prefix}        Status: {self.status}\n" \
                 f"{prefix}    created_at: {self.created_at}\n" \
                 f"{prefix}    updated_at: {self.updated_at}\n"
        if verbose:
            output = output + f"{prefix}       payload: {self.payload}\n"
        return output

    def print(self, prefix="", verbose=False, associated_entities_to_show=None):
        print(self.__str__(prefix=prefix, verbose=verbose))


class DbValidation(DbBase, EntityBase):
    __tablename__ = 'validation'
    id = Column(String(), primary_key=True)
    file_id = Column(String(), ForeignKey('file.id'), nullable=False)
    job_id = Column(String(), nullable=False)
    status = Column(String(), nullable=False)
    results = Column(String(), nullable=False)
    validation_started_at = Column(DateTime(), nullable=False)
    validation_ended_at = Column(DateTime(), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False, onupdate=datetime.utcnow)

    file = relationship("DbFile", back_populates='validations')

    def __str__(self, prefix="", verbose=False):
        output = colored(f"{prefix}Validation {self.id}\n", 'yellow') + \
                 f"{prefix}                  File ID: {self.file_id}\n" \
                 f"{prefix}                   Job ID: {self.job_id}\n" \
                 f"{prefix}                   Status: {self.status}\n" \
                 f"{prefix}    validation_started_at: {self.validation_started_at}\n" \
                 f"{prefix}      validation_ended_at: {self.validation_ended_at}\n" \
                 f"{prefix}               created_at: {self.created_at}\n" \
                 f"{prefix}               updated_at: {self.updated_at}\n"
        if verbose:
            output = output + f"{prefix}                  results: {self.results}\n"
        return output

    def print(self, prefix="", verbose=False, associated_entities_to_show=None):
        print(self.__str__(prefix=prefix, verbose=verbose))


DbUploadArea.files = relationship('DbFile', order_by=DbFile.id, back_populates='upload_area')
DbFile.checksums = relationship('DbChecksum', order_by=DbChecksum.created_at, back_populates='file')
DbFile.validations = relationship('DbValidation', order_by=DbValidation.created_at, back_populates='file')
DbFile.notifications = relationship('DbNotification', order_by=DbNotification.created_at, back_populates='file')
