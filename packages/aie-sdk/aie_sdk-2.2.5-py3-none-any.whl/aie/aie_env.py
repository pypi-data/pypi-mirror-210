#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import aie
import aie.g_var as g_var
from aie.error import AIEError, AIEErrorCode


class AIEEnv(object):
    @staticmethod
    def init(debug_level):
        AIEEnv.__setDebugLevel(debug_level)

        aie.client.interactive_session.InteractiveSession.create()
        AIEEnv.__setPorjectId()

        print("计算资源初始化完成.")

    @staticmethod
    def cancelAllInteractiveJobs():
        confirm = input("该操作会停止当前账号所有正在运行中的在线交互任务，请输入yes/no: ")
        if confirm == "yes":
            print("在线交互任务取消中...")
            aie.client.interactive_session.InteractiveSession.cancelAllJobs()
            print("操作完成")
        else:
            print("操作取消")

    @staticmethod
    def __setPorjectId():
        if os.getenv(g_var.JupyterEnv.PROJECT_ID) is not None:
            project_id = os.getenv(g_var.JupyterEnv.PROJECT_ID)
            if project_id.isdigit():
                g_var.set_var(g_var.GVarKey.Project.PROJECT_ID,
                              int(project_id))
            else:
                print("warning: 项目ID获取失败，设置为-1")
                g_var.set_var(g_var.GVarKey.Project.PROJECT_ID, -1)
        else:
            g_var.set_var(g_var.GVarKey.Project.PROJECT_ID, -1)

    @staticmethod
    def __setDebugLevel(debug_level):
        g_var.set_var(g_var.GVarKey.Log.LOG_LEVEL, debug_level)

    @staticmethod
    def getCurrentUserInteractiveSession():
        if not g_var.has_var(g_var.GVarKey.InteractiveSession.INTERACTIVE_SESSION_ID):
            raise AIEError(AIEErrorCode.ENVIRONMENT_INIT_ERROR,
                           "计算资源ID获取失败，请先调用 aie.Initialize() 创建")
        return g_var.get_var(g_var.GVarKey.InteractiveSession.INTERACTIVE_SESSION_ID)

    @staticmethod
    def getCurrentUserProjectId():
        if not g_var.has_var(g_var.GVarKey.Project.PROJECT_ID):
            raise AIEError(AIEErrorCode.ENVIRONMENT_INIT_ERROR,
                           "项目projectId获取失败")
        return g_var.get_var(g_var.GVarKey.Project.PROJECT_ID)

    @staticmethod
    def getDebugLevel():
        return g_var.get_var(g_var.GVarKey.Log.LOG_LEVEL)
