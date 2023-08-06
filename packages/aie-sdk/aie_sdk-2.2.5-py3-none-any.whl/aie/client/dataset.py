#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
from aie.error import AIEError, AIEErrorCode
from .client import BaseClient, Client
from .endpoints import Endpoints, MarianaDataResource
import oss2
import urllib


class Dataset(BaseClient):
    def __init__(self, name):
        self.name = name
        self.file_entries = []
        self.dataset_id = -1

    class StatusCode():
        PUBLISHING = 0
        COMPLETED = 6
        FAILED = -1

    class Status():
        PUBLISHING = "发布中"
        COMPLETED = "发布完成"
        FAILED = "发布失败"

    def upload(self, file, suffix):
        headers = {"Content-Type": "application/json"}

        get_sts_token_url = Endpoints.MARIANA_DATA + \
            MarianaDataResource.GET_STS_TOKEN.format(suffix)
        response = super(Dataset, self).get(
            get_sts_token_url, headers).json()
        if response["code"] != 0:
            raise AIEError(response["code"], response["message"])

        ak = response["module"]["accessKeyId"]
        sk = response["module"]["accessKeySecret"]
        token = response["module"]["securityToken"]
        region = response["module"]["region"]
        bucket = response["module"]["bucket"]
        file_key = response["module"]["fileKey"]
        file_name = os.path.basename(file)

        auth = oss2.StsAuth(ak, sk, token)
        oss_bucket = oss2.Bucket(
            auth, "http://{}-internal.aliyuncs.com".format(region), bucket)
        headers = {
            "Content-Disposition": f"attachment;filename={urllib.parse.quote(file_name)}"}
        oss_bucket.put_object_from_file(file_key, file, headers)

        self.file_entries.append({
            "name": file_name,
            "uri": "oss://{}/{}".format(bucket, file_key)
        })

    def publish(self):
        headers = {"Content-Type": "application/json"}

        publish_url = Endpoints.MARIANA_DATA + MarianaDataResource.PUBLISH
        payload = {
            "datasets": [{"name": self.name, "entries": self.file_entries}]
        }
        response = super(Dataset, self).post(
            publish_url, headers, payload).json()
        if response["code"] != 0:
            raise AIEError(response["code"], response["message"])

        self.dataset_id = response["module"][0]

    def __toStatus(self, status):
        if status == Dataset.StatusCode.COMPLETED:
            return Dataset.Status.COMPLETED
        elif status == Dataset.StatusCode.PUBLISHING:
            return Dataset.Status.PUBLISHING
        else:
            return Dataset.Status.FAILED

    def status(self):
        if self.dataset_id == -1:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "dataset_id未初始化")

        headers = {"Content-Type": "application/json"}

        status_url = Endpoints.MARIANA_DATA + \
            MarianaDataResource.GET_PUBLISH_STATUS.format(self.dataset_id)
        response = super(Dataset, self).get(
            status_url, headers).json()
        if response["code"] != 0:
            raise AIEError(response["code"], response["message"])

        status = response["module"]["publishStatus"]
        return self.__toStatus(status)

    def active(self):
        status = self.status()
        return status == Dataset.Status.PUBLISHING
