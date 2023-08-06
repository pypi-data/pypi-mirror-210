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


class Terrain(FunctionNode):
    @staticmethod
    def aspect(input: aie.Image) -> aie.Image:
        if input is not None and not isinstance(input, aie.Image):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR, f"input 只支持aie.Image类型参数, 传入类型为{type(input)}"
            )

        invoke_args = {
            "input": input,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        if "input" not in invoke_args:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "参数input不能为空")

        return FunctionHelper.apply("Terrain.aspect", "aie.Image", invoke_args)

    @staticmethod
    def slope(input: aie.Image) -> aie.Image:
        if input is not None and not isinstance(input, aie.Image):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR, f"input 只支持aie.Image类型参数, 传入类型为{type(input)}"
            )

        invoke_args = {
            "input": input,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        if "input" not in invoke_args:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "参数input不能为空")

        return FunctionHelper.apply("Terrain.slope", "aie.Image", invoke_args)

    @staticmethod
    def hillshade(
        input: aie.Image, azimuth: [int, float] = 270, elevation: [int, float] = 45
    ) -> aie.Image:
        if input is not None and not isinstance(input, aie.Image):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR, f"input 只支持aie.Image类型参数, 传入类型为{type(input)}"
            )

        if azimuth is not None and not isinstance(azimuth, (int, float)):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"azimuth 只支持(int,float)类型参数, 传入类型为{type(azimuth)}",
            )

        if elevation is not None and not isinstance(elevation, (int, float)):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"elevation 只支持(int,float)类型参数, 传入类型为{type(elevation)}",
            )

        invoke_args = {
            "input": input,
            "azimuth": azimuth,
            "elevation": elevation,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        if "input" not in invoke_args:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "参数input不能为空")

        return FunctionHelper.apply("Terrain.hillshade", "aie.Image", invoke_args)
