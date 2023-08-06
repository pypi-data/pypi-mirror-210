#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os

import requests
from aie.error import AIEError, AIEErrorCode
import aie.g_var as g_var
import aie

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class BaseClient(object):
    @staticmethod
    def __append_extra_hdrs(hdrs):
        hdrs["x-aie-auth-token"] = aie.auth.Authenticate.getCurrentUserToken()

        project_id = os.getenv(g_var.JupyterEnv.PROJECT_ID, "local")
        hdrs['x-aie-client-name'] = f"aie-sdk@Project-{project_id}"
        return hdrs

    @staticmethod
    def post(url, hdrs, data, append_extra_hdrs=True):
        if append_extra_hdrs:
            hdrs = BaseClient.__append_extra_hdrs(hdrs)

        if aie.aie_env.AIEEnv.getDebugLevel() == g_var.LogLevel.DEBUG_LEVEL:
            print(
                f"BaseClient::post request. url: {url}, headers: {json.dumps(hdrs)}, data: {json.dumps(data)}")

        resp = requests.post(url=url, headers=hdrs, timeout=(600, 600),
                             json=data, verify=False)

        if resp.status_code != 200:
            if "401 Authorization Required" in resp.text:
                raise AIEError(AIEErrorCode.ENVIRONMENT_INIT_ERROR,
                               f"未授权或者个人token失效，请先调用 aie.Authenticate() 进行授权")
            else:
                raise AIEError(AIEErrorCode.DEFAULT_INTERNAL_ERROR,
                               "", f"http请求错误: {resp.text}")

        if aie.aie_env.AIEEnv.getDebugLevel() == g_var.LogLevel.DEBUG_LEVEL:
            print(
                f"BaseClient::post response. url: {url}, response: {resp.json()}")

        return resp

    @staticmethod
    def get(url, hdrs, append_extra_hdrs=True):
        if append_extra_hdrs:
            hdrs = BaseClient.__append_extra_hdrs(hdrs)

        if aie.aie_env.AIEEnv.getDebugLevel() == g_var.LogLevel.DEBUG_LEVEL:
            print(
                f"BaseClient::get request. url: {url}, headers: {json.dumps(hdrs)}")

        resp = requests.get(url=url, headers=hdrs,
                            timeout=(600, 600), verify=False)

        if resp.status_code != 200:
            if "401 Authorization Required" in resp.text:
                raise AIEError(AIEErrorCode.ENVIRONMENT_INIT_ERROR,
                               f"未授权或者个人token失效，请先调用 aie.Authenticate() 进行授权")
            else:
                raise AIEError(AIEErrorCode.DEFAULT_INTERNAL_ERROR,
                               "", f"http请求错误: {resp.text}")

        if aie.aie_env.AIEEnv.getDebugLevel() == g_var.LogLevel.DEBUG_LEVEL:
            print(
                f"BaseClient::get response. url: {url}, response: {resp.json()}")

        return resp

    @staticmethod
    def delete(url, hdrs, append_extra_hdrs=True):
        if append_extra_hdrs:
            hdrs = BaseClient.__append_extra_hdrs(hdrs)

        if aie.aie_env.AIEEnv.getDebugLevel() == g_var.LogLevel.DEBUG_LEVEL:
            print(
                f"BaseClient::delete request. url: {url}, headers: {json.dumps(hdrs)}")

        resp = requests.delete(url=url, headers=hdrs,
                               timeout=(600, 600), verify=False)

        if resp.status_code != 200:
            if "401 Authorization Required" in resp.text:
                raise AIEError(AIEErrorCode.ENVIRONMENT_INIT_ERROR,
                               f"未授权或者个人token失效，请先调用 aie.Authenticate() 进行授权")
            else:
                raise AIEError(AIEErrorCode.DEFAULT_INTERNAL_ERROR,
                               "", f"http请求错误: {resp.text}")

        if aie.aie_env.AIEEnv.getDebugLevel() == g_var.LogLevel.DEBUG_LEVEL:
            print(
                f"BaseClient::delete response. url: {url}, response: {resp.json()}")

        return resp


class Client(BaseClient):
    class ResponseCode(object):
        OK = 0
        ERROR = -1

    @staticmethod
    def __append_extra_body(data):
        options = {}
        if "options" in data:
            options = json.loads(data["options"])

        options["sessionId"] = aie.aie_env.AIEEnv.getCurrentUserInteractiveSession()
        options["projectId"] = aie.aie_env.AIEEnv.getCurrentUserProjectId()
        data["options"] = json.dumps(options)
        return data

    @staticmethod
    def post(url, data):
        headers = {"Content-Type": "application/json"}
        data = Client.__append_extra_body(data)
        resp = super(Client, Client).post(url, headers, data)
        response_data = resp.json()
        if "object" in response_data:
            value = json.loads(response_data["object"])
            if value["code"] != Client.ResponseCode.OK:
                extrainfo = {}
                if "requestId" in value:
                    extrainfo["requestId"] = value["requestId"]
                raise AIEError(
                    value["code"], value["message"], json.dumps(extrainfo))
            return value
        else:
            raise AIEError(AIEErrorCode.DEFAULT_INTERNAL_ERROR,
                           "", json.dumps(response_data))

    @staticmethod
    def get(url):
        headers = {"Content-Type": "application/json"}
        resp = super(Client, Client).get(url, headers)
        response_data = resp.json()
        if "object" in response_data:
            value = json.loads(response_data["object"])
            if value["code"] != Client.ResponseCode.OK:
                extrainfo = {}
                if "requestId" in value:
                    extrainfo["requestId"] = value["requestId"]
                raise AIEError(
                    value["code"], value["message"], json.dumps(extrainfo))
            return value
        else:
            raise AIEError(AIEErrorCode.DEFAULT_INTERNAL_ERROR,
                           "", json.dumps(response_data))

    @staticmethod
    def delete(url):
        headers = {"Content-Type": "application/json"}
        resp = super(Client, Client).delete(url, headers)
        response_data = resp.json()
        if "object" in response_data:
            value = json.loads(response_data["object"])
            if value["code"] != Client.ResponseCode.OK:
                extrainfo = {}
                if "requestId" in value:
                    extrainfo["requestId"] = value["requestId"]
                raise AIEError(
                    value["code"], value["message"], json.dumps(extrainfo))
            return value
        else:
            raise AIEError(AIEErrorCode.DEFAULT_INTERNAL_ERROR,
                           "",  json.dumps(response_data))
