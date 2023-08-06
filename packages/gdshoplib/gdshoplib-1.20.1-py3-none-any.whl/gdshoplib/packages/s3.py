from typing import Optional

import boto3
from botocore.exceptions import ClientError
from pydantic import BaseModel

from gdshoplib.core.settings import S3Settings


class S3:
    def __init__(self, data):
        self.data = data
        self.content = None
        self.s3_settings = S3Settings()
        self.__session = None
        self.__client = None
        self.__iter = None

    @property
    def session(self):
        if not self.__session:
            self.__session = boto3.session.Session()

        return self.__session

    @property
    def s3(self):
        if not self.__client:
            self.__client = self.session.client(
                service_name="s3",
                endpoint_url=self.s3_settings.ENDPOINT_URL,
                aws_access_key_id=self.s3_settings.ACCESS_KEY,
                aws_secret_access_key=self.s3_settings.SECRET_KEY,
            )
        return self.__client

    def put(self):
        return self.s3.put_object(
            Bucket=self.s3_settings.BUCKET_NAME,
            Key=self.data.file_key,
            Body=self.data.content,
            ACL="public-read",
            StorageClass="ICE",
            ContentType=self.data.mime,
        )

    def exists(self, key=None):
        try:
            self.s3.head_object(
                Bucket=self.s3_settings.BUCKET_NAME, Key=key or self.data.file_key
            )
        except ClientError:
            return False
        else:
            return True

    def __iter__(self):
        paginator = self.s3.get_paginator("list_objects_v2")
        iterator = paginator.paginate(
            Bucket=self.s3_settings.BUCKET_NAME, PaginationConfig={"PageSize": 100}
        )
        self.__iter = iter([*(page["Contents"] for page in iterator)][0])
        return self

    def __next__(self):
        object = next(self.__iter)
        return object

    def search(self, pattern=None):
        if pattern:
            paginator = self.s3.get_paginator("list_objects_v2")
            page_iterator = paginator.paginate(Bucket=self.s3_settings.BUCKET_NAME)
            return page_iterator.search(pattern)
        return iter(self)

    def clean(self, pattern=None):
        for object in self.search(pattern):
            self.delete(object["Key"])

    def get(self, key=None):
        try:
            return self.s3.get_object(
                Bucket=self.s3_settings.BUCKET_NAME, Key=key or self.data.file_key
            )
        except ClientError as ex:
            if ex.response["Error"]["Code"] == "NoSuchKey":
                return None
            raise ex

    def delete(self, key=None):
        return self.s3.delete_object(
            Bucket=self.s3_settings.BUCKET_NAME, Key=key or self.data.file_key
        )

    def __str__(self) -> str:
        return f"{self.__class__}: {self.data.file_key}"

    def __repr__(self) -> str:
        return f"{self.__class__}: {self.data.file_key}"


class FileInfoModel(BaseModel):
    id: str
    format: str
    prefix: Optional[str]


class SimpleS3Data:
    def __init__(
        self,
        content,
        /,
        file_key,
        mime="text/plain",
        file_info: FileInfoModel = None,
        parent=None,
    ):
        self.content = content
        self._file_key = file_key
        self.mime = mime
        self.parent = parent
        self.file_info = None

        if file_info:
            self.file_info = (
                file_info
                if isinstance(file_info, FileInfoModel)
                else FileInfoModel(**file_info)
            )

    @property
    def file_key(self):
        if self.file_info:
            sku = self.parent.sku if self.parent else ""
            prefix = self.file_info.prefix or ""
            return f"{prefix}.{sku}.{self.file_info.id}.{self.file_info.format.lower()}"
        else:
            return self._file_key
