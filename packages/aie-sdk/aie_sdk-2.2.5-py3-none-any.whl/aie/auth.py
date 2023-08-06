#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import aie.g_var as g_var
from aie.client import Endpoints
from aie.error import AIEError, AIEErrorCode


class Authenticate(object):
    class ClientId(object):
        USER_STD = "user_std"
        ALIYUN_JUPYTER = "aliyun_jupyter"

    @staticmethod
    def getClientEnvironment():
        if os.getenv(g_var.JupyterEnv.TOKEN) is not None:
            return Authenticate.ClientId.ALIYUN_JUPYTER
        else:
            return Authenticate.ClientId.USER_STD

    @staticmethod
    def __displayAuthPromt():
        print("请将以下地址粘贴到Web浏览器中，访问授权页面，并将个人token粘贴到输入框中")
        print("\t", Endpoints.AUTH_PORTAL_PAGE)

    @staticmethod
    def __getTokenFromJupyter():
        token = os.getenv(g_var.JupyterEnv.TOKEN)
        if token is None:
            raise AIEError(AIEErrorCode.ENVIRONMENT_INIT_ERROR,
                           "云平台环境token获取失败")
        return token

    @staticmethod
    def auth(token=None):
        client_id = Authenticate.getClientEnvironment()

        cred = {}
        cred["client_id"] = client_id
        if token is not None:
            cred["token"] = token
        else:
            if client_id == Authenticate.ClientId.ALIYUN_JUPYTER:
                token = Authenticate.__getTokenFromJupyter()
                cred["token"] = token
            else:
                Authenticate.__displayAuthPromt()
                token = input("个人token: ")
                cred["token"] = token

        g_var.set_var(g_var.GVarKey.Authenticate.CLIENT_ID, cred["client_id"])
        g_var.set_var(g_var.GVarKey.Authenticate.TOKEN, cred["token"])

    @staticmethod
    def getCurrentUserToken():
        if not g_var.has_var(g_var.GVarKey.Authenticate.CLIENT_ID):
            raise AIEError(AIEErrorCode.ENVIRONMENT_INIT_ERROR,
                           "客户端ID获取失败，请先调用 aie.Authenticate() 进行授权")

        client_id = g_var.get_var(g_var.GVarKey.Authenticate.CLIENT_ID)
        token = ""
        if client_id == Authenticate.ClientId.ALIYUN_JUPYTER:
            token = Authenticate.__getTokenFromJupyter()
        else:
            if not g_var.has_var(g_var.GVarKey.Authenticate.TOKEN):
                raise AIEError(AIEErrorCode.ENVIRONMENT_INIT_ERROR,
                               "个人token获取失败，请先调用 aie.Authenticate() 进行授权")
            token = g_var.get_var(g_var.GVarKey.Authenticate.TOKEN)
        return token
