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


class ConfusionMatrix(FunctionNode):
    def __init__(self, array: list) -> aie.ConfusionMatrix:
        if array is not None and not isinstance(array, list):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR, f"array 只支持list类型参数, 传入类型为{type(array)}"
            )

        invoke_args = {
            "array": array,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        if "array" not in invoke_args:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "参数array不能为空")

        super(ConfusionMatrix, self).__init__(
            "ConfusionMatrix.constructors", invoke_args
        )

    def accuracy(self) -> object:
        invoke_args = {
            "input": self,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        return FunctionHelper.apply("ConfusionMatrix.accuracy", "object", invoke_args)

    def consumersAccuracy(self) -> object:
        invoke_args = {
            "input": self,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        return FunctionHelper.apply(
            "ConfusionMatrix.consumersAccuracy", "object", invoke_args
        )

    def fscore(self, beta: [int, float] = 1.0) -> object:
        if beta is not None and not isinstance(beta, (int, float)):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR, f"beta 只支持(int,float)类型参数, 传入类型为{type(beta)}"
            )

        invoke_args = {
            "input": self,
            "beta": beta,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        return FunctionHelper.apply("ConfusionMatrix.fscore", "object", invoke_args)

    def kappa(self) -> object:
        invoke_args = {
            "input": self,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        return FunctionHelper.apply("ConfusionMatrix.kappa", "object", invoke_args)

    def producersAccuracy(self) -> object:
        invoke_args = {
            "input": self,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        return FunctionHelper.apply(
            "ConfusionMatrix.producersAccuracy", "object", invoke_args
        )

    def array(self) -> object:
        invoke_args = {
            "input": self,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        return FunctionHelper.apply("ConfusionMatrix.array", "object", invoke_args)
