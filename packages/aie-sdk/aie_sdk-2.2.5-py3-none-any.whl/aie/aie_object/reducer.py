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


class Reducer(FunctionNode):
    def combine(
        self, reducer2: aie.Reducer, outputPrefix: str = "", sharedInputs: bool = False
    ) -> aie.Reducer:
        if reducer2 is not None and not isinstance(reducer2, aie.Reducer):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"reducer2 只支持aie.Reducer类型参数, 传入类型为{type(reducer2)}",
            )

        if outputPrefix is not None and not isinstance(outputPrefix, str):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"outputPrefix 只支持str类型参数, 传入类型为{type(outputPrefix)}",
            )

        if sharedInputs is not None and not isinstance(sharedInputs, bool):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"sharedInputs 只支持bool类型参数, 传入类型为{type(sharedInputs)}",
            )

        invoke_args = {
            "reducer1": self,
            "reducer2": reducer2,
            "outputPrefix": outputPrefix,
            "sharedInputs": sharedInputs,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        if "reducer2" not in invoke_args:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "参数reducer2不能为空")

        return FunctionHelper.apply("Reducer.combine", "aie.Reducer", invoke_args)

    @staticmethod
    def histogram(
        maxBuckets: int = None, minBucketWidth: [int, float] = None, maxRaw: int = None
    ) -> aie.Reducer:
        if maxBuckets is not None and not isinstance(maxBuckets, int):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"maxBuckets 只支持int类型参数, 传入类型为{type(maxBuckets)}",
            )

        if minBucketWidth is not None and not isinstance(minBucketWidth, (int, float)):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"minBucketWidth 只支持(int,float)类型参数, 传入类型为{type(minBucketWidth)}",
            )

        if maxRaw is not None and not isinstance(maxRaw, int):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR, f"maxRaw 只支持int类型参数, 传入类型为{type(maxRaw)}"
            )

        invoke_args = {
            "maxBuckets": maxBuckets,
            "minBucketWidth": minBucketWidth,
            "maxRaw": maxRaw,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        return FunctionHelper.apply("Reducer.histogram", "aie.Reducer", invoke_args)

    @staticmethod
    def count() -> aie.Reducer:
        invoke_args = {}

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        return FunctionHelper.apply("Reducer.count", "aie.Reducer", invoke_args)

    @staticmethod
    def max(numInputs: int = 1) -> aie.Reducer:
        if numInputs is not None and not isinstance(numInputs, int):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR, f"numInputs 只支持int类型参数, 传入类型为{type(numInputs)}"
            )

        invoke_args = {
            "numInputs": numInputs,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        return FunctionHelper.apply("Reducer.max", "aie.Reducer", invoke_args)

    @staticmethod
    def mean() -> aie.Reducer:
        invoke_args = {}

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        return FunctionHelper.apply("Reducer.mean", "aie.Reducer", invoke_args)

    @staticmethod
    def median(
        maxBuckets: int = None, minBucketWidth: [int, float] = None, maxRaw: int = None
    ) -> aie.Reducer:
        if maxBuckets is not None and not isinstance(maxBuckets, int):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"maxBuckets 只支持int类型参数, 传入类型为{type(maxBuckets)}",
            )

        if minBucketWidth is not None and not isinstance(minBucketWidth, (int, float)):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"minBucketWidth 只支持(int,float)类型参数, 传入类型为{type(minBucketWidth)}",
            )

        if maxRaw is not None and not isinstance(maxRaw, int):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR, f"maxRaw 只支持int类型参数, 传入类型为{type(maxRaw)}"
            )

        invoke_args = {
            "maxBuckets": maxBuckets,
            "minBucketWidth": minBucketWidth,
            "maxRaw": maxRaw,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        return FunctionHelper.apply("Reducer.median", "aie.Reducer", invoke_args)

    @staticmethod
    def min(numInputs: int = 1) -> aie.Reducer:
        if numInputs is not None and not isinstance(numInputs, int):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR, f"numInputs 只支持int类型参数, 传入类型为{type(numInputs)}"
            )

        invoke_args = {
            "numInputs": numInputs,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        return FunctionHelper.apply("Reducer.min", "aie.Reducer", invoke_args)

    @staticmethod
    def minMax() -> aie.Reducer:
        invoke_args = {}

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        return FunctionHelper.apply("Reducer.minMax", "aie.Reducer", invoke_args)

    @staticmethod
    def mode(
        maxBuckets: int = None, minBucketWidth: [int, float] = None, maxRaw: int = None
    ) -> aie.Reducer:
        if maxBuckets is not None and not isinstance(maxBuckets, int):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"maxBuckets 只支持int类型参数, 传入类型为{type(maxBuckets)}",
            )

        if minBucketWidth is not None and not isinstance(minBucketWidth, (int, float)):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"minBucketWidth 只支持(int,float)类型参数, 传入类型为{type(minBucketWidth)}",
            )

        if maxRaw is not None and not isinstance(maxRaw, int):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR, f"maxRaw 只支持int类型参数, 传入类型为{type(maxRaw)}"
            )

        invoke_args = {
            "maxBuckets": maxBuckets,
            "minBucketWidth": minBucketWidth,
            "maxRaw": maxRaw,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        return FunctionHelper.apply("Reducer.mode", "aie.Reducer", invoke_args)

    @staticmethod
    def product() -> aie.Reducer:
        invoke_args = {}

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        return FunctionHelper.apply("Reducer.product", "aie.Reducer", invoke_args)

    @staticmethod
    def stdDev() -> aie.Reducer:
        invoke_args = {}

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        return FunctionHelper.apply("Reducer.stdDev", "aie.Reducer", invoke_args)

    @staticmethod
    def sum() -> aie.Reducer:
        invoke_args = {}

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        return FunctionHelper.apply("Reducer.sum", "aie.Reducer", invoke_args)

    @staticmethod
    def variance() -> aie.Reducer:
        invoke_args = {}

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        return FunctionHelper.apply("Reducer.variance", "aie.Reducer", invoke_args)

    @staticmethod
    def allNonZero() -> aie.Reducer:
        invoke_args = {}

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        return FunctionHelper.apply("Reducer.allNonZero", "aie.Reducer", invoke_args)

    @staticmethod
    def anyNonZero() -> aie.Reducer:
        invoke_args = {}

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        return FunctionHelper.apply("Reducer.anyNonZero", "aie.Reducer", invoke_args)

    @staticmethod
    def bitwiseAnd() -> aie.Reducer:
        invoke_args = {}

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        return FunctionHelper.apply("Reducer.bitwiseAnd", "aie.Reducer", invoke_args)

    @staticmethod
    def bitwiseOr() -> aie.Reducer:
        invoke_args = {}

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        return FunctionHelper.apply("Reducer.bitwiseOr", "aie.Reducer", invoke_args)

    @staticmethod
    def sampleStdDev() -> aie.Reducer:
        invoke_args = {}

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        return FunctionHelper.apply("Reducer.sampleStdDev", "aie.Reducer", invoke_args)

    @staticmethod
    def sampleVariance() -> aie.Reducer:
        invoke_args = {}

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        return FunctionHelper.apply(
            "Reducer.sampleVariance", "aie.Reducer", invoke_args
        )

    @staticmethod
    def histogram(buckets: int) -> aie.Reducer:
        if buckets is not None and not isinstance(buckets, int):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR, f"buckets 只支持int类型参数, 传入类型为{type(buckets)}"
            )

        invoke_args = {
            "buckets": buckets,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        if "buckets" not in invoke_args:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "参数buckets不能为空")

        return FunctionHelper.apply("Reducer.histogram", "aie.Reducer", invoke_args)

    @staticmethod
    def fixedHistogram(
        min: [int, float], max: [int, float], buckets: int
    ) -> aie.Reducer:
        if min is not None and not isinstance(min, (int, float)):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR, f"min 只支持(int,float)类型参数, 传入类型为{type(min)}"
            )

        if max is not None and not isinstance(max, (int, float)):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR, f"max 只支持(int,float)类型参数, 传入类型为{type(max)}"
            )

        if buckets is not None and not isinstance(buckets, int):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR, f"buckets 只支持int类型参数, 传入类型为{type(buckets)}"
            )

        invoke_args = {
            "min": min,
            "max": max,
            "buckets": buckets,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        if "min" not in invoke_args:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "参数min不能为空")

        if "max" not in invoke_args:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "参数max不能为空")

        if "buckets" not in invoke_args:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "参数buckets不能为空")

        return FunctionHelper.apply(
            "Reducer.fixedHistogram", "aie.Reducer", invoke_args
        )

    @staticmethod
    def linearFit() -> aie.Reducer:
        invoke_args = {}

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        return FunctionHelper.apply("Reducer.linearFit", "aie.Reducer", invoke_args)

    @staticmethod
    def linearRegression() -> aie.Reducer:
        invoke_args = {}

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        return FunctionHelper.apply(
            "Reducer.linearRegression", "aie.Reducer", invoke_args
        )

    @staticmethod
    def pearsonsCorrelation() -> aie.Reducer:
        invoke_args = {}

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        return FunctionHelper.apply(
            "Reducer.pearsonsCorrelation", "aie.Reducer", invoke_args
        )

    @staticmethod
    def spearmansCorrelation() -> aie.Reducer:
        invoke_args = {}

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        return FunctionHelper.apply(
            "Reducer.spearmansCorrelation", "aie.Reducer", invoke_args
        )

    @staticmethod
    def ridgeRegression(regParam: [int, float] = 0.1) -> aie.Reducer:
        if regParam is not None and not isinstance(regParam, (int, float)):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"regParam 只支持(int,float)类型参数, 传入类型为{type(regParam)}",
            )

        invoke_args = {
            "regParam": regParam,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        return FunctionHelper.apply(
            "Reducer.ridgeRegression", "aie.Reducer", invoke_args
        )

    @staticmethod
    def lassoRegression(regParam: [int, float] = 0.1) -> aie.Reducer:
        if regParam is not None and not isinstance(regParam, (int, float)):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"regParam 只支持(int,float)类型参数, 传入类型为{type(regParam)}",
            )

        invoke_args = {
            "regParam": regParam,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        return FunctionHelper.apply(
            "Reducer.lassoRegression", "aie.Reducer", invoke_args
        )
