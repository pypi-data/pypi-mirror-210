#!/usr/bin/env python
# -*- coding: utf-8 -*-

import uuid
import os


def newUUID():
    return str(uuid.uuid1())


class Endpoints():
    DEFAULT_HOST = "https://engine-aiearth.aliyun.com"
    HOST = os.getenv("SDK_CLIENT_HOST", DEFAULT_HOST)

    MAP = HOST + "/ep/v1alpha/map"
    MAP_VECTOR = HOST + "/ep/v1alpha/vector"
    SDK_GATEWAY = HOST + "/ep/v1alpha/api"
    INTERACTIVE_SESSION = HOST + "/ep/v1alpha/interactive_session"
    AUTH_PORTAL_PAGE = HOST + "/#/utility/auth-token"

    MARIANA_DATA = "http://dataset-upload.engine-aiearth.aliyun.com"

    ML_PROXY_HOST = HOST + "/ep/v1alpha/mlproxy/"

    DEFAULT_STAC_ENDPOINT = "http://172.16.2.12:8038"
    STAC_ENDPOINT = os.getenv("STAC_ENDPOINT", DEFAULT_STAC_ENDPOINT)


class SdkGatewayResource():
    class Task():
        START = "/task/start"
        STATUS = "/task/status/{}"
        CANCEL = "/task/cancel/{}"

    class Maps():
        GET_MAP_ID = "/maps/getMapId"


class InteractiveSessionResource():
    CREATE = "/job/session/create"
    QUERY = "/job/session/query?session_id={}"
    EXEC = "/job/session/script/exec"
    CANCEL_ALL = "/job/session/script/cancelAll"


class MarianaDataResource():
    GET_STS_TOKEN = "/dataapi/public/oss/sts/token/get?suffix={}&type=DATASET"
    PUBLISH = "/dataapi/public/dataset/publish"
    GET_PUBLISH_STATUS = "/dataapi/public/dataset/status?id={}"
