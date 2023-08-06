#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json


class AIEErrorCode(object):
    DEFAULT_INTERNAL_ERROR = 12306000

    # user define
    ENVIRONMENT_INIT_ERROR = 22306001
    ARGS_ERROR = 22306002
    JOB_CANCELLED = 22306003


class AIEError(Exception):
    DEFAULT_ERROR_MESSAGE = "系统未知异常"

    def __init__(self, code: int = AIEErrorCode.DEFAULT_INTERNAL_ERROR, message: str = "", troubleshooting_information: str = ""):
        debug_info = ""
        if troubleshooting_information != json.dumps({}):
            debug_info = troubleshooting_information
        if str(code).startswith("2"):
            super().__init__("[AIEError]: {}, {}. {}".format(
                code, message, debug_info))
        else:
            super().__init__("{}. {}".format(
                AIEError.DEFAULT_ERROR_MESSAGE, debug_info))
