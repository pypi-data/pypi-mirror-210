import fnmatch
import json
import logging
from datetime import datetime

import boto3
import pendulum
from pydantic import BaseModel, HttpUrl, ValidationError
from tabulate import tabulate

from .common import session_maker, validate_response

logger = logging.getLogger(__file__)

KST = pendulum.timezone("Asia/Seoul")


################################################################
# Model for S3 Database
################################################################
class ValueModel(BaseModel):
    _filename_field = "url"

    url: HttpUrl
    method: str = None
    created_at: datetime = datetime.now().astimezone(KST)
    finished_at: datetime = None
    modified_count: int = 1


################################################################
# S3 Common Helpers
################################################################
def list_objects(
    bucket: str,
    prefix: str = None,
    pattern: str = None,
    session: boto3.Session = None,
    session_opts: dict = None,
):
    # correct
    prefix = prefix if prefix else ""
    pattern = "*" + pattern if pattern else pattern

    # get session
    session = session if session else session_maker(session_opts=session_opts)
    client = session.client("s3")

    # get list of objects
    contents = []
    paginator = client.get_paginator("list_objects_v2")
    for response in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for content in response.get("Contents", []):
            if not pattern or fnmatch.fnmatch(content["Key"], pattern):
                contents.append(content)

    return contents


def delete_objects(
    bucket: str,
    prefix: str,
    pattern: str = None,
    confirm: bool = True,
    session: boto3.Session = None,
    session_opts: dict = None,
):
    # correct
    prefix = prefix if prefix else ""

    # get session
    session = session if session else session_maker(session_opts=session_opts)
    client = session.client("s3")

    # list objects to delete
    contents = list_objects(bucket=bucket, prefix=prefix, pattern=pattern, session=session)
    n_objects = len(contents)

    if n_objects == 0:
        logger.warning("no objects to delete. exit!")
        return

    if confirm:
        print(f"Find {n_objects} Objects to Delete.\n" + tabulate(contents))
        answer = input("Are You Sure? (yes or no) ")
        if answer != "yes":
            print("Exit!")
            return

    # delete
    if len(contents) > 0:
        # delete objects
        delete = {"Objects": [{"Key": content["Key"]} for content in contents]}
        response = client.delete_objects(Bucket=bucket, Delete=delete)
        return response["Deleted"]

    raise FileNotFoundError(f"no pattern '{pattern}' in prefix '{bucket}/{prefix}'!")


################################################################
# S3 as a Database
################################################################
class Database:
    def __init__(
        self,
        bucket: str,
        prefix: str,
        Model: BaseModel = ValueModel,
        session: boto3.Session = None,
        session_opts: dict = None,
    ):
        # props
        self.bucket = bucket
        self.prefix = prefix
        self.Model = Model

        # session
        self.session = session if session else session_maker(session_opts=session_opts)
        self.client = self.session.client("s3")
        self.resource = self.session.resource("s3")
        self.Bucket = self.resource.Bucket(self.bucket)

    def keys(self, patterns: list = ["*"], unfinished=None):
        objects = self._list_objects(patterns=patterns)
        if unfinished is None:
            return [self._trim_key(obj.key) for obj in objects]

        # filter unfinished, finished
        keys = [obj.key for obj in objects]
        objects = [self._deserialize(body) for obj in objects for body in obj.get()["Body"]]
        if unfinished:
            return [
                self._trim_key(key)
                for key, obj in zip(keys, objects)
                if obj is not None and obj.created_at is not None
            ]
        else:
            return [
                self._trim_key(key) for key, obj in zip(keys, objects) if obj is not None and obj.created_at is None
            ]

    def clean(self):
        """Delete Wrong Schema Keys"""
        objects = self._list_objects()
        for obj in objects:
            for body in obj.get()["Body"]:
                try:
                    value = self._deserialize(body)
                except Exception as ex:
                    logger.error(ex)
                    raise ex
                if value is None:
                    key = self._trim_key(obj.key)
                    logger.warning(f"object {key} has wrong schema - removed!")
                    print(key)
                    self.delete(key=key)

    def _list_objects(self, patterns: list = ["*"]):
        return [
            obj
            for obj in self.Bucket.objects.filter(Prefix=self.prefix)
            if any([fnmatch.fnmatch(obj.key, "/".join([self.prefix, pat])) for pat in patterns])
        ]

    def set(
        self,
        key: str,
        url: HttpUrl,
        method: str = None,
        finished_at: datetime = None,
        overwrite: bool = True,
    ):
        if finished_at and not isinstance(finished_at, datetime):
            finished_at = datetime.fromisoformat(finished_at)
        value = ValueModel(url=url, method=method, finished_at=finished_at)
        return self._set(key=key, value=value, overwrite=overwrite)

    def _set(self, key: str, value: ValueModel, overwrite=True):
        current = self._get(key)
        if current is not None:
            if not overwrite:
                raise FileExistsError(f"object {self._generate_full_key(key)} exists!")
            value.modified_count = current.modified_count + 1
            value.created_at = current.created_at

        params = {
            "Bucket": self.bucket,
            "Key": self._generate_full_key(key),
            "Body": self._serialize(value),
        }

        try:
            response = self.client.put_object(**params)
            validate_response(response)
            return response
        except Exception as ex:
            logger.error(ex)
            raise ex

    def get(
        self,
        key: str,
        if_modified_since: datetime = None,
        if_unmodified_since: datetime = None,
    ):
        value = self._get(key=key, if_modified_since=if_modified_since, if_unmodified_since=if_unmodified_since)
        if value is None:
            return
        return value.dict()

    def _get(
        self,
        key: str,
        if_modified_since: datetime = None,
        if_unmodified_since: datetime = None,
    ):
        params = {
            "Bucket": self.bucket,
            "Key": self._generate_full_key(key),
        }
        if if_modified_since:
            if not isinstance(if_modified_since, datetime):
                if_modified_since = datetime.fromisoformat(if_modified_since)
            params.update({"IfModifiedSince": if_modified_since})
        if if_unmodified_since:
            if not isinstance(if_unmodified_since, datetime):
                if_unmodified_since = datetime.fromisoformat(if_unmodified_since)
            params.update({"IfUnmodifiedSince": if_unmodified_since})

        try:
            response = self.client.get_object(**params)
            validate_response(response)
        except self.client.exceptions.NoSuchKey:
            return

        for body in response["Body"]:
            return self._deserialize(body)

    def delete(self, key: str):
        Object = {
            "Bucket": self.bucket,
            "Key": self._generate_full_key(key),
        }
        response = self.client.delete_object(**Object)
        validate_response(response, success_codes=[200, 204])
        return response

    def _generate_full_key(self, key):
        return "/".join([self.prefix, key.strip("/")])

    def _trim_key(self, full_key):
        return full_key.replace(f"{self.prefix}/", "", 1)

    def _serialize(self, value):
        return value.json()

    def _deserialize(self, body):
        try:
            _body = json.loads(body)
            return self.Model(**_body)
        except ValidationError:
            logger.warning(f"skip! deserialize failed, {body}")
            return
        except Exception as ex:
            logger.error(ex)
            raise ex
