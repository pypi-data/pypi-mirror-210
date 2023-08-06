#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from aie.error import AIEError, AIEErrorCode

G_VAR = {}


class JupyterEnv(object):
    TOKEN = "JUPYTER_TOKEN"
    PROJECT_ID = "JUPYTERHUB_SERVER_NAME"


class LogLevel(object):
    DEBUG_LEVEL = "debug"
    INFO_LEVEL = "info"


class GVarKey(object):
    class Authenticate(object):
        CLIENT_ID = "client_id"
        TOKEN = "token"

    class InteractiveSession(object):
        INTERACTIVE_SESSION_ID = "interactive_session_id"

    class Project(object):
        PROJECT_ID = "project_id"

    class Log(object):
        LOG_LEVEL = "log_level"


def has_var(key):
    return key in G_VAR


def get_var(key):
    if key not in G_VAR:
        raise AIEError(AIEErrorCode.DEFAULT_INTERNAL_ERROR,
                       "", f"G_VAR {key} not found")
    return G_VAR[key]


def set_var(key, value):
    global G_VAR
    G_VAR[key] = value
