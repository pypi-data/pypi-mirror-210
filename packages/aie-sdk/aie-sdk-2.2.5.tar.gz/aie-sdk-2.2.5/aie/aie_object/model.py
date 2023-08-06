#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import annotations

import abc
import inspect
from typing import Union

import aie
from aie.variable_node import VariableNode
from aie.function_node import FunctionNode
from aie.customfunction_node import CustomFunctionNode
from aie.function_helper import FunctionHelper
from aie.error.aie_error import AIEError, AIEErrorCode


class Model(FunctionNode):
    def __init__(self, modelName) -> aie.Model:
        self.modelName = modelName
        super(Model, self).__init__("Model.load", {"modelName": modelName})

    def predict(self, src: aie.Image, dst: aie.Image = None) -> aie.Image:
        if src is not None and not isinstance(src, aie.Image):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR, f"src 只支持aie.Image类型参数, 传入类型为{type(src)}"
            )

        if dst is not None and not isinstance(dst, aie.Image):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR, f"dst 只支持aie.Image类型参数, 传入类型为{type(dst)}"
            )

        invoke_args = {
            "model": self,
            "src": src,
            "dst": dst,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        if "src" not in invoke_args:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "参数src不能为空")

        return FunctionHelper.apply("Model.predict", "aie.Image", invoke_args)
