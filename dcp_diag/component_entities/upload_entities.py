from datetime import datetime

import boto3
from botocore.errorfactory import ClientError
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, Session
from termcolor import colored

from dcplib.config import Config

from dcp_diag.component_entities import EntityBase
from .. import DcpDiagException

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
    id = Column(Integer(), primary_key=True)
    uuid = Column(String(), nullable=False)
    bucket_name = Column(String(), nullable=False)
    status = Column(String(), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False, onupdate=datetime.utcnow)

    def __str__(self, prefix="", verbose=False):
        return colored(f"{prefix}Upload Area {self.id}: {self.uuid}\n", 'blue') + \
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
    id = Column(Integer(), primary_key=True)
    s3_key = Column(String(), nullable=False)
    s3_etag = Column(String(), nullable=True)
    upload_area_id = Column(Integer(), ForeignKey('upload_area.id'), nullable=False)
    name = Column(String(), nullable=False)
    size = Column(Integer(), nullable=False)
    checksums = Column(JSON(), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False, onupdate=datetime.utcnow)

    upload_area = relationship("DbUploadArea", back_populates="files")

    def __str__(self, prefix="", verbose=False):
        output = colored(f"{prefix}File {self.id}: {self.s3_key} with etag={self.s3_etag}\n", 'green') + \
            f"{prefix}            s3_key: {self.s3_key}\n" \
            f"{prefix}           s3_etag: {self.s3_etag}\n" \
            f"{prefix}    Upload Area ID: {self.upload_area_id}\n" \
            f"{prefix}              Name: {self.name}\n" \
            f"{prefix}              Size: {self.size}\n" \
            f"{prefix}        created_at: {self.created_at}\n" \
            f"{prefix}        updated_at: {self.updated_at}\n"
        if verbose:
            output = output + f"{prefix}         checksums: {self.checksums}\n"
        return output

    def print(self, prefix="", verbose=False, associated_entities_to_show=None):

        # Hack: keep session alive, otherwise we get:
        # Parent instance <DbFile at 0x10674a6a0> is not bound to a Session; lazy load operation of attribute
        # 'notifications' cannot proceed (Background on this error at: http://sqlalche.me/e/bhk3)
        session = Session.object_session(self)

        print(self.__str__(prefix=prefix, verbose=verbose))
        if associated_entities_to_show:
            prefix = f"\t{prefix}"
            if 'checksums' in associated_entities_to_show or 'all' in associated_entities_to_show:
                for checksum in self.checksum_records:
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
    checksum_started_at = Column(DateTime(), nullable=False)
    checksum_ended_at = Column(DateTime(), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False, onupdate=datetime.utcnow)

    file = relationship("DbFile", back_populates='checksum_records')

    def __str__(self, prefix="", verbose=False):
        output = colored(f"{prefix}Checksum {self.id}\n", 'cyan') + \
                 f"{prefix}                File ID: {self.file_id}\n" \
                 f"{prefix}                 Job ID: {self.job_id}\n" \
                 f"{prefix}                 Status: {self.status}\n" \
                 f"{prefix}    checksum_started_at: {self.checksum_started_at}\n" \
                 f"{prefix}      checksum_ended_at: {self.checksum_ended_at}\n" \
                 f"{prefix}             created_at: {self.created_at}\n" \
                 f"{prefix}             updated_at: {self.updated_at}\n"
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
        if associated_entities_to_show:
            prefix = f"\t{prefix}"
            if 'batch_jobs' in associated_entities_to_show or 'all' in associated_entities_to_show:
                BatchJob.find_by_id(self.job_id).print(prefix=prefix, verbose=verbose,
                                                       associated_entities_to_show=associated_entities_to_show)


class BatchJob(EntityBase):

    @classmethod
    def find_by_id(cls, job_id):
        batch = boto3.client('batch')
        response = batch.describe_jobs(jobs=[job_id])
        assert 'jobs' in response
        if len(response['jobs']) == 0:
            raise DcpDiagException(f"Sorry I couldn't find job \"{job_id}\"")
        assert len(response['jobs']) == 1
        return cls(aws_job_data=response['jobs'][0])

    def __init__(self, aws_job_data):
        self.job = aws_job_data

    @property
    def id(self):
        return self.job.get('jobId')

    def __str__(self, prefix="", verbose=False):
        output = ""
        try:
            output += \
                colored(f"{prefix}Batch Job {self.id}\n", 'blue') + \
                f"{prefix}    Job Name        {self.job.get('jobName')}\n" + \
                f"{prefix}    Job Id          {self.job.get('jobId')}\n" + \
                f"{prefix}    Job Queue       {self.job.get('jobQueue')}\n" + \
                f"{prefix}    Job Definition  {self.job.get('jobDefinition')}\n" + \
                f"{prefix}    Status          {self.job.get('status')}\n" + \
                f"{prefix}    Status Reason   {self.job.get('statusReason')}\n" + \
                f"{prefix}    Created at      {self._datetime(self.job, 'createdAt')}\n" + \
                f"{prefix}    Started at      {self._datetime(self.job, 'startedAt')}\n" + \
                f"{prefix}    Stopped at      {self._datetime(self.job, 'stoppedAt')}\n"

            if 'startedAt' in self.job and 'stoppedAt' in self.job:
                duration = (self.job.get('stoppedAt') - self.job.get('startedAt')) / 1000
                output += f"{prefix}    Duration        {duration}s\n"

            output += \
                f"{prefix}    Container:\n" + \
                f"{prefix}        Image                   {self.job['container'].get('image')}\n" + \
                f"{prefix}        IvCPUs                  {self.job['container'].get('vcpus')}\n" + \
                f"{prefix}        Memory                  {self.job['container'].get('memory')}\n" + \
                f"{prefix}        Command                 {' '.join(self.job['container'].get('command'))}\n" + \
                f"{prefix}        Reason                  {self.job['container'].get('reason')}\n" + \
                f"{prefix}        Container Instance ARN  {self.job['container'].get('containerInstanceArn')}\n" + \
                f"{prefix}        Task ARN                {self.job['container'].get('taskArn')}\n" + \
                f"{prefix}        Log Stream Name         {self.job['container'].get('logStreamName')}\n"

            if 'attempts' in self.job:
                output += f"{prefix}    Attempts:\n"
                for idx, attempt in enumerate(self.job['attempts']):
                    output += \
                        f"{prefix}\tAttempt #{idx}\n" + \
                        f"{prefix}\tStarted At:     {self._datetime(attempt, 'startedAt')}\n" + \
                        f"{prefix}\tStopped At:     {self._datetime(attempt, 'stoppedAt')}\n" + \
                        f"{prefix}\tStatus Reason:  {attempt['statusReason']}\n" + \
                        f"{prefix}\tContainer:\n" + \
                        f"{prefix}\t    Container Reason:  {attempt['container'].get('reason')}\n"
        except KeyError:
            pass
        return output

    def print(self, prefix="", verbose=False, associated_entities_to_show=None):
        print(self.__str__(prefix=prefix, verbose=verbose))
        if associated_entities_to_show:
            prefix = f"\t{prefix}"
            if 'logs' in associated_entities_to_show or 'all' in associated_entities_to_show:
                log_stream_name = self.job['container']['logStreamName']
                log = CloudWatchLog(log_group_name='/aws/batch/job', log_stream_name=log_stream_name)
                log.print(prefix=prefix, verbose=verbose,
                          associated_entities_to_show=associated_entities_to_show)

    @staticmethod
    def _datetime(dictionary, key):
        if key in dictionary and dictionary[key]:
            return datetime.fromtimestamp(dictionary[key]/1000).strftime('%Y-%m-%d %H:%M:%S')
        else:
            return ""


class CloudWatchLog(EntityBase):

    def __init__(self, log_group_name, log_stream_name):
        self.log_group_name = log_group_name
        self.log_stream_name = log_stream_name
        self.logs = boto3.client('logs')

    def __str__(self, prefix="", verbose=False):
        output = colored(f"{prefix}Log:\n", 'red')
        if self.log_stream_name:
            try:
                response = self.logs.get_log_events(logGroupName=self.log_group_name,
                                                    logStreamName=self.log_stream_name)
                assert 'events' in response
                for event in response['events']:
                    output += event['message'] + "\n"
            except ClientError:
                pass
        else:
            output += "No log yet.\n"
        return output

    def print(self, prefix="", verbose=False, associated_entities_to_show=None):
        print(self.__str__(prefix=prefix, verbose=verbose))


DbUploadArea.files = relationship('DbFile', order_by=DbFile.id, back_populates='upload_area')
DbFile.checksum_records = relationship('DbChecksum', order_by=DbChecksum.created_at, back_populates='file')
DbFile.validations = relationship('DbValidation', order_by=DbValidation.created_at, back_populates='file')
DbFile.notifications = relationship('DbNotification', order_by=DbNotification.created_at, back_populates='file')
