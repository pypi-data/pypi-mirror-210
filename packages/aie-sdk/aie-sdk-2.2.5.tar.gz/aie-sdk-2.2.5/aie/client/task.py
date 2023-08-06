#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import requests
from .endpoints import *
from .client import Client
import aie
from aie.serialize import serializer
from aie.error import AIEError, AIEErrorCode


class Task(object):
    class StatusCode(object):
        WAITING = "waiting"
        RUNNING = "running"
        COMPLETED = "completed"
        FAILED = "failed"
        CANCEL_REQUEST = "cancel_request"
        CANCELLED = "cancelled"

    class Status(object):
        WAITING = "等待中"
        RUNNING = "运行中"
        COMPLETED = "任务已完成"
        FAILED = "任务失败"
        CANCEL_REQUEST = "任务取消中"
        CANCELLED = "任务已取消"

    def __init__(self, obj, options=None):
        self.request_id = newUUID()
        self.expr = serializer.encode(obj)
        self.options = options

    def start(self):
        data = {"requestId": self.request_id,
                "expr": self.expr}

        if self.options is not None:
            data["options"] = json.dumps(self.options)

        headers = {"Content-Type": "application/json"}
        url = Endpoints.SDK_GATEWAY + SdkGatewayResource.Task.START
        Client.post(url, data)

    def __toStatus(self, status):
        if status == Task.StatusCode.WAITING:
            return Task.Status.WAITING
        elif status == Task.StatusCode.RUNNING:
            return Task.Status.RUNNING
        elif status == Task.StatusCode.COMPLETED:
            return Task.Status.COMPLETED
        elif status == Task.StatusCode.FAILED:
            return Task.Status.FAILED
        elif status == Task.StatusCode.CANCEL_REQUEST:
            return Task.Status.CANCEL_REQUEST
        elif status == Task.StatusCode.CANCELLED:
            return Task.Status.CANCELLED
        else:
            raise AIEError(AIEErrorCode.DEFAULT_INTERNAL_ERROR,
                           "", f"status {status} 未知")

    def status(self):
        headers = {"Content-Type": "application/json"}
        url = Endpoints.SDK_GATEWAY + \
            SdkGatewayResource.Task.STATUS.format(self.request_id)
        response = Client.get(url)
        status = response["status"]
        return self.__toStatus(status)

    def active(self):
        status = self.status()
        return status in (Task.Status.WAITING, Task.Status.RUNNING)

    def cancel(self):
        headers = {"Content-Type": "application/json"}
        url = Endpoints.SDK_GATEWAY + \
            SdkGatewayResource.Task.CANCEL.format(self.request_id)
        Client.delete(url)
