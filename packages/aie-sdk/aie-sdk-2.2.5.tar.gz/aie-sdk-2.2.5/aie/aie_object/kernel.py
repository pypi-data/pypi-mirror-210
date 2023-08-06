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


class Kernel(FunctionNode):
    @staticmethod
    def chebyshev(
        radius: [int, float],
        units: str = "pixels",
        normalize: bool = False,
        magnitude: [int, float] = 1.0,
    ) -> aie.Kernel:
        if radius is not None and not isinstance(radius, (int, float)):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"radius 只支持(int,float)类型参数, 传入类型为{type(radius)}",
            )

        if units is not None and not isinstance(units, str):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR, f"units 只支持str类型参数, 传入类型为{type(units)}"
            )

        if normalize is not None and not isinstance(normalize, bool):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"normalize 只支持bool类型参数, 传入类型为{type(normalize)}",
            )

        if magnitude is not None and not isinstance(magnitude, (int, float)):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"magnitude 只支持(int,float)类型参数, 传入类型为{type(magnitude)}",
            )

        invoke_args = {
            "radius": radius,
            "units": units,
            "normalize": normalize,
            "magnitude": magnitude,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        if "radius" not in invoke_args:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "参数radius不能为空")

        return FunctionHelper.apply("Kernel.chebyshev", "aie.Kernel", invoke_args)

    @staticmethod
    def circle(
        radius: [int, float],
        units: str = "pixels",
        normalize: bool = False,
        magnitude: [int, float] = 1.0,
    ) -> aie.Kernel:
        if radius is not None and not isinstance(radius, (int, float)):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"radius 只支持(int,float)类型参数, 传入类型为{type(radius)}",
            )

        if units is not None and not isinstance(units, str):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR, f"units 只支持str类型参数, 传入类型为{type(units)}"
            )

        if normalize is not None and not isinstance(normalize, bool):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"normalize 只支持bool类型参数, 传入类型为{type(normalize)}",
            )

        if magnitude is not None and not isinstance(magnitude, (int, float)):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"magnitude 只支持(int,float)类型参数, 传入类型为{type(magnitude)}",
            )

        invoke_args = {
            "radius": radius,
            "units": units,
            "normalize": normalize,
            "magnitude": magnitude,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        if "radius" not in invoke_args:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "参数radius不能为空")

        return FunctionHelper.apply("Kernel.circle", "aie.Kernel", invoke_args)

    @staticmethod
    def compass(normalize: bool = False, magnitude: [int, float] = 1.0) -> aie.Kernel:
        if normalize is not None and not isinstance(normalize, bool):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"normalize 只支持bool类型参数, 传入类型为{type(normalize)}",
            )

        if magnitude is not None and not isinstance(magnitude, (int, float)):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"magnitude 只支持(int,float)类型参数, 传入类型为{type(magnitude)}",
            )

        invoke_args = {
            "normalize": normalize,
            "magnitude": magnitude,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        return FunctionHelper.apply("Kernel.compass", "aie.Kernel", invoke_args)

    @staticmethod
    def cross(
        radius: [int, float],
        units: str = "pixels",
        normalize: bool = False,
        magnitude: [int, float] = 1.0,
    ) -> aie.Kernel:
        if radius is not None and not isinstance(radius, (int, float)):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"radius 只支持(int,float)类型参数, 传入类型为{type(radius)}",
            )

        if units is not None and not isinstance(units, str):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR, f"units 只支持str类型参数, 传入类型为{type(units)}"
            )

        if normalize is not None and not isinstance(normalize, bool):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"normalize 只支持bool类型参数, 传入类型为{type(normalize)}",
            )

        if magnitude is not None and not isinstance(magnitude, (int, float)):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"magnitude 只支持(int,float)类型参数, 传入类型为{type(magnitude)}",
            )

        invoke_args = {
            "radius": radius,
            "units": units,
            "normalize": normalize,
            "magnitude": magnitude,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        if "radius" not in invoke_args:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "参数radius不能为空")

        return FunctionHelper.apply("Kernel.cross", "aie.Kernel", invoke_args)

    @staticmethod
    def diamond(
        radius: [int, float],
        units: str = "pixels",
        normalize: bool = False,
        magnitude: [int, float] = 1.0,
    ) -> aie.Kernel:
        if radius is not None and not isinstance(radius, (int, float)):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"radius 只支持(int,float)类型参数, 传入类型为{type(radius)}",
            )

        if units is not None and not isinstance(units, str):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR, f"units 只支持str类型参数, 传入类型为{type(units)}"
            )

        if normalize is not None and not isinstance(normalize, bool):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"normalize 只支持bool类型参数, 传入类型为{type(normalize)}",
            )

        if magnitude is not None and not isinstance(magnitude, (int, float)):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"magnitude 只支持(int,float)类型参数, 传入类型为{type(magnitude)}",
            )

        invoke_args = {
            "radius": radius,
            "units": units,
            "normalize": normalize,
            "magnitude": magnitude,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        if "radius" not in invoke_args:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "参数radius不能为空")

        return FunctionHelper.apply("Kernel.diamond", "aie.Kernel", invoke_args)

    @staticmethod
    def euclidean(
        radius: [int, float],
        units: str = "pixels",
        normalize: bool = False,
        magnitude: [int, float] = 1.0,
    ) -> aie.Kernel:
        if radius is not None and not isinstance(radius, (int, float)):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"radius 只支持(int,float)类型参数, 传入类型为{type(radius)}",
            )

        if units is not None and not isinstance(units, str):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR, f"units 只支持str类型参数, 传入类型为{type(units)}"
            )

        if normalize is not None and not isinstance(normalize, bool):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"normalize 只支持bool类型参数, 传入类型为{type(normalize)}",
            )

        if magnitude is not None and not isinstance(magnitude, (int, float)):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"magnitude 只支持(int,float)类型参数, 传入类型为{type(magnitude)}",
            )

        invoke_args = {
            "radius": radius,
            "units": units,
            "normalize": normalize,
            "magnitude": magnitude,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        if "radius" not in invoke_args:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "参数radius不能为空")

        return FunctionHelper.apply("Kernel.euclidean", "aie.Kernel", invoke_args)

    @staticmethod
    def fixed(weights: list, normalize: bool = False) -> aie.Kernel:
        if weights is not None and not isinstance(weights, list):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR, f"weights 只支持list类型参数, 传入类型为{type(weights)}"
            )

        if normalize is not None and not isinstance(normalize, bool):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"normalize 只支持bool类型参数, 传入类型为{type(normalize)}",
            )

        invoke_args = {
            "weights": weights,
            "normalize": normalize,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        if "weights" not in invoke_args:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "参数weights不能为空")

        return FunctionHelper.apply("Kernel.fixed", "aie.Kernel", invoke_args)

    @staticmethod
    def gaussian(
        radius: [int, float],
        sigma: [int, float] = 1.0,
        units: str = "pixels",
        normalize: bool = False,
        magnitude: [int, float] = 1.0,
    ) -> aie.Kernel:
        if radius is not None and not isinstance(radius, (int, float)):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"radius 只支持(int,float)类型参数, 传入类型为{type(radius)}",
            )

        if sigma is not None and not isinstance(sigma, (int, float)):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR, f"sigma 只支持(int,float)类型参数, 传入类型为{type(sigma)}"
            )

        if units is not None and not isinstance(units, str):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR, f"units 只支持str类型参数, 传入类型为{type(units)}"
            )

        if normalize is not None and not isinstance(normalize, bool):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"normalize 只支持bool类型参数, 传入类型为{type(normalize)}",
            )

        if magnitude is not None and not isinstance(magnitude, (int, float)):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"magnitude 只支持(int,float)类型参数, 传入类型为{type(magnitude)}",
            )

        invoke_args = {
            "radius": radius,
            "sigma": sigma,
            "units": units,
            "normalize": normalize,
            "magnitude": magnitude,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        if "radius" not in invoke_args:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "参数radius不能为空")

        return FunctionHelper.apply("Kernel.gaussian", "aie.Kernel", invoke_args)

    @staticmethod
    def kirsch(normalize: bool = False, magnitude: [int, float] = 1.0) -> aie.Kernel:
        if normalize is not None and not isinstance(normalize, bool):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"normalize 只支持bool类型参数, 传入类型为{type(normalize)}",
            )

        if magnitude is not None and not isinstance(magnitude, (int, float)):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"magnitude 只支持(int,float)类型参数, 传入类型为{type(magnitude)}",
            )

        invoke_args = {
            "normalize": normalize,
            "magnitude": magnitude,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        return FunctionHelper.apply("Kernel.kirsch", "aie.Kernel", invoke_args)

    @staticmethod
    def laplacian4(
        normalize: bool = False, magnitude: [int, float] = 1.0
    ) -> aie.Kernel:
        if normalize is not None and not isinstance(normalize, bool):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"normalize 只支持bool类型参数, 传入类型为{type(normalize)}",
            )

        if magnitude is not None and not isinstance(magnitude, (int, float)):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"magnitude 只支持(int,float)类型参数, 传入类型为{type(magnitude)}",
            )

        invoke_args = {
            "normalize": normalize,
            "magnitude": magnitude,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        return FunctionHelper.apply("Kernel.laplacian4", "aie.Kernel", invoke_args)

    @staticmethod
    def laplacian8(
        normalize: bool = False, magnitude: [int, float] = 1.0
    ) -> aie.Kernel:
        if normalize is not None and not isinstance(normalize, bool):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"normalize 只支持bool类型参数, 传入类型为{type(normalize)}",
            )

        if magnitude is not None and not isinstance(magnitude, (int, float)):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"magnitude 只支持(int,float)类型参数, 传入类型为{type(magnitude)}",
            )

        invoke_args = {
            "normalize": normalize,
            "magnitude": magnitude,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        return FunctionHelper.apply("Kernel.laplacian8", "aie.Kernel", invoke_args)

    @staticmethod
    def manhattan(
        radius: [int, float],
        units: str = "pixels",
        normalize: bool = False,
        magnitude: [int, float] = 1.0,
    ) -> aie.Kernel:
        if radius is not None and not isinstance(radius, (int, float)):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"radius 只支持(int,float)类型参数, 传入类型为{type(radius)}",
            )

        if units is not None and not isinstance(units, str):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR, f"units 只支持str类型参数, 传入类型为{type(units)}"
            )

        if normalize is not None and not isinstance(normalize, bool):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"normalize 只支持bool类型参数, 传入类型为{type(normalize)}",
            )

        if magnitude is not None and not isinstance(magnitude, (int, float)):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"magnitude 只支持(int,float)类型参数, 传入类型为{type(magnitude)}",
            )

        invoke_args = {
            "radius": radius,
            "units": units,
            "normalize": normalize,
            "magnitude": magnitude,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        if "radius" not in invoke_args:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "参数radius不能为空")

        return FunctionHelper.apply("Kernel.manhattan", "aie.Kernel", invoke_args)

    @staticmethod
    def plus(
        radius: [int, float],
        units: str = "pixels",
        normalize: bool = False,
        magnitude: [int, float] = 1.0,
    ) -> aie.Kernel:
        if radius is not None and not isinstance(radius, (int, float)):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"radius 只支持(int,float)类型参数, 传入类型为{type(radius)}",
            )

        if units is not None and not isinstance(units, str):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR, f"units 只支持str类型参数, 传入类型为{type(units)}"
            )

        if normalize is not None and not isinstance(normalize, bool):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"normalize 只支持bool类型参数, 传入类型为{type(normalize)}",
            )

        if magnitude is not None and not isinstance(magnitude, (int, float)):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"magnitude 只支持(int,float)类型参数, 传入类型为{type(magnitude)}",
            )

        invoke_args = {
            "radius": radius,
            "units": units,
            "normalize": normalize,
            "magnitude": magnitude,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        if "radius" not in invoke_args:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "参数radius不能为空")

        return FunctionHelper.apply("Kernel.plus", "aie.Kernel", invoke_args)

    @staticmethod
    def prewitt(normalize: bool = False, magnitude: [int, float] = 1.0) -> aie.Kernel:
        if normalize is not None and not isinstance(normalize, bool):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"normalize 只支持bool类型参数, 传入类型为{type(normalize)}",
            )

        if magnitude is not None and not isinstance(magnitude, (int, float)):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"magnitude 只支持(int,float)类型参数, 传入类型为{type(magnitude)}",
            )

        invoke_args = {
            "normalize": normalize,
            "magnitude": magnitude,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        return FunctionHelper.apply("Kernel.prewitt", "aie.Kernel", invoke_args)

    @staticmethod
    def rectangle(
        xRadius: [int, float],
        yRadius: [int, float],
        units: str = "pixels",
        normalize: bool = False,
        magnitude: [int, float] = 1.0,
    ) -> aie.Kernel:
        if xRadius is not None and not isinstance(xRadius, (int, float)):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"xRadius 只支持(int,float)类型参数, 传入类型为{type(xRadius)}",
            )

        if yRadius is not None and not isinstance(yRadius, (int, float)):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"yRadius 只支持(int,float)类型参数, 传入类型为{type(yRadius)}",
            )

        if units is not None and not isinstance(units, str):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR, f"units 只支持str类型参数, 传入类型为{type(units)}"
            )

        if normalize is not None and not isinstance(normalize, bool):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"normalize 只支持bool类型参数, 传入类型为{type(normalize)}",
            )

        if magnitude is not None and not isinstance(magnitude, (int, float)):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"magnitude 只支持(int,float)类型参数, 传入类型为{type(magnitude)}",
            )

        invoke_args = {
            "xRadius": xRadius,
            "yRadius": yRadius,
            "units": units,
            "normalize": normalize,
            "magnitude": magnitude,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        if "xRadius" not in invoke_args:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "参数xRadius不能为空")

        if "yRadius" not in invoke_args:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "参数yRadius不能为空")

        return FunctionHelper.apply("Kernel.rectangle", "aie.Kernel", invoke_args)

    @staticmethod
    def roberts(normalize: bool = False, magnitude: [int, float] = 1.0) -> aie.Kernel:
        if normalize is not None and not isinstance(normalize, bool):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"normalize 只支持bool类型参数, 传入类型为{type(normalize)}",
            )

        if magnitude is not None and not isinstance(magnitude, (int, float)):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"magnitude 只支持(int,float)类型参数, 传入类型为{type(magnitude)}",
            )

        invoke_args = {
            "normalize": normalize,
            "magnitude": magnitude,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        return FunctionHelper.apply("Kernel.roberts", "aie.Kernel", invoke_args)

    @staticmethod
    def sobel(normalize: bool = False, magnitude: [int, float] = 1.0) -> aie.Kernel:
        if normalize is not None and not isinstance(normalize, bool):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"normalize 只支持bool类型参数, 传入类型为{type(normalize)}",
            )

        if magnitude is not None and not isinstance(magnitude, (int, float)):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"magnitude 只支持(int,float)类型参数, 传入类型为{type(magnitude)}",
            )

        invoke_args = {
            "normalize": normalize,
            "magnitude": magnitude,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        return FunctionHelper.apply("Kernel.sobel", "aie.Kernel", invoke_args)

    @staticmethod
    def square(
        radius: [int, float],
        units: str = "pixels",
        normalize: bool = False,
        magnitude: [int, float] = 1.0,
    ) -> aie.Kernel:
        if radius is not None and not isinstance(radius, (int, float)):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"radius 只支持(int,float)类型参数, 传入类型为{type(radius)}",
            )

        if units is not None and not isinstance(units, str):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR, f"units 只支持str类型参数, 传入类型为{type(units)}"
            )

        if normalize is not None and not isinstance(normalize, bool):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"normalize 只支持bool类型参数, 传入类型为{type(normalize)}",
            )

        if magnitude is not None and not isinstance(magnitude, (int, float)):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"magnitude 只支持(int,float)类型参数, 传入类型为{type(magnitude)}",
            )

        invoke_args = {
            "radius": radius,
            "units": units,
            "normalize": normalize,
            "magnitude": magnitude,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        if "radius" not in invoke_args:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "参数radius不能为空")

        return FunctionHelper.apply("Kernel.square", "aie.Kernel", invoke_args)

    def add(self, kernel2: aie.Kernel, normalize: bool = False) -> aie.Kernel:
        if kernel2 is not None and not isinstance(kernel2, aie.Kernel):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"kernel2 只支持aie.Kernel类型参数, 传入类型为{type(kernel2)}",
            )

        if normalize is not None and not isinstance(normalize, bool):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"normalize 只支持bool类型参数, 传入类型为{type(normalize)}",
            )

        invoke_args = {
            "kernel1": self,
            "kernel2": kernel2,
            "normalize": normalize,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        if "kernel2" not in invoke_args:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "参数kernel2不能为空")

        return FunctionHelper.apply("Kernel.add", "aie.Kernel", invoke_args)

    def subtract(self, kernel2: aie.Kernel, normalize: bool = False) -> aie.Kernel:
        if kernel2 is not None and not isinstance(kernel2, aie.Kernel):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"kernel2 只支持aie.Kernel类型参数, 传入类型为{type(kernel2)}",
            )

        if normalize is not None and not isinstance(normalize, bool):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"normalize 只支持bool类型参数, 传入类型为{type(normalize)}",
            )

        invoke_args = {
            "kernel1": self,
            "kernel2": kernel2,
            "normalize": normalize,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        if "kernel2" not in invoke_args:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "参数kernel2不能为空")

        return FunctionHelper.apply("Kernel.subtract", "aie.Kernel", invoke_args)

    def multiply(self, kernel2: aie.Kernel, normalize: bool = False) -> aie.Kernel:
        if kernel2 is not None and not isinstance(kernel2, aie.Kernel):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"kernel2 只支持aie.Kernel类型参数, 传入类型为{type(kernel2)}",
            )

        if normalize is not None and not isinstance(normalize, bool):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"normalize 只支持bool类型参数, 传入类型为{type(normalize)}",
            )

        invoke_args = {
            "kernel1": self,
            "kernel2": kernel2,
            "normalize": normalize,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        if "kernel2" not in invoke_args:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "参数kernel2不能为空")

        return FunctionHelper.apply("Kernel.multiply", "aie.Kernel", invoke_args)

    def divide(self, kernel2: aie.Kernel, normalize: bool = False) -> aie.Kernel:
        if kernel2 is not None and not isinstance(kernel2, aie.Kernel):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"kernel2 只支持aie.Kernel类型参数, 传入类型为{type(kernel2)}",
            )

        if normalize is not None and not isinstance(normalize, bool):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"normalize 只支持bool类型参数, 传入类型为{type(normalize)}",
            )

        invoke_args = {
            "kernel1": self,
            "kernel2": kernel2,
            "normalize": normalize,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        if "kernel2" not in invoke_args:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "参数kernel2不能为空")

        return FunctionHelper.apply("Kernel.divide", "aie.Kernel", invoke_args)

    def inverse(self) -> aie.Kernel:
        invoke_args = {
            "kernel": self,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        return FunctionHelper.apply("Kernel.inverse", "aie.Kernel", invoke_args)

    def rotate(self, rotations: int) -> aie.Kernel:
        if rotations is not None and not isinstance(rotations, int):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR, f"rotations 只支持int类型参数, 传入类型为{type(rotations)}"
            )

        invoke_args = {
            "kernel": self,
            "rotations": rotations,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        if "rotations" not in invoke_args:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "参数rotations不能为空")

        return FunctionHelper.apply("Kernel.rotate", "aie.Kernel", invoke_args)
