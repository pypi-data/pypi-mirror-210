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


class Classifier(FunctionNode):
    def __init__(self, preResult: str = "") -> aie.Classifier:
        if preResult is not None and not isinstance(preResult, str):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR, f"preResult 只支持str类型参数, 传入类型为{type(preResult)}"
            )

        invoke_args = {
            "preResult": preResult,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        super(Classifier, self).__init__("Classifier.constructors", invoke_args)

    def train(
        self, features: aie.FeatureCollection, classProperty: str, inputProperties: list
    ) -> aie.Classifier:
        if features is not None and not isinstance(features, aie.FeatureCollection):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"features 只支持aie.FeatureCollection类型参数, 传入类型为{type(features)}",
            )

        if classProperty is not None and not isinstance(classProperty, str):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"classProperty 只支持str类型参数, 传入类型为{type(classProperty)}",
            )

        if inputProperties is not None and not isinstance(inputProperties, list):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"inputProperties 只支持list类型参数, 传入类型为{type(inputProperties)}",
            )

        invoke_args = {
            "input": self,
            "features": features,
            "classProperty": classProperty,
            "inputProperties": inputProperties,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        if "features" not in invoke_args:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "参数features不能为空")

        if "classProperty" not in invoke_args:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "参数classProperty不能为空")

        if "inputProperties" not in invoke_args:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "参数inputProperties不能为空")

        clf = FunctionHelper.apply("Classifier.train", "aie.Classifier", invoke_args)

        obj = aie.client.InteractiveSession.classifierTrain(clf)
        invoke_args["preResult"] = obj
        clf = FunctionHelper.apply("Classifier.train", "aie.Classifier", invoke_args)

        return clf

    @staticmethod
    def linearsvm() -> aie.Classifier:
        invoke_args = {}

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        return FunctionHelper.apply(
            "Classifier.linearsvm", "aie.Classifier", invoke_args
        )

    @staticmethod
    def libsvm(
        svmType: str = "C_SVC",
        kernelType: str = "LINEAR",
        shrinking: bool = True,
        degree: int = 3,
        gamma: [int, float] = None,
        coef0: [int, float] = 0.0,
        cost: [int, float] = 1.0,
        nu: [int, float] = 0.5,
        terminationEpsilon: [int, float] = 0.001,
        lossEpsilon: [int, float] = 0.1,
    ) -> aie.Classifier:
        if svmType is not None and not isinstance(svmType, str):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR, f"svmType 只支持str类型参数, 传入类型为{type(svmType)}"
            )

        if kernelType is not None and not isinstance(kernelType, str):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"kernelType 只支持str类型参数, 传入类型为{type(kernelType)}",
            )

        if shrinking is not None and not isinstance(shrinking, bool):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"shrinking 只支持bool类型参数, 传入类型为{type(shrinking)}",
            )

        if degree is not None and not isinstance(degree, int):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR, f"degree 只支持int类型参数, 传入类型为{type(degree)}"
            )

        if gamma is not None and not isinstance(gamma, (int, float)):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR, f"gamma 只支持(int,float)类型参数, 传入类型为{type(gamma)}"
            )

        if coef0 is not None and not isinstance(coef0, (int, float)):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR, f"coef0 只支持(int,float)类型参数, 传入类型为{type(coef0)}"
            )

        if cost is not None and not isinstance(cost, (int, float)):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR, f"cost 只支持(int,float)类型参数, 传入类型为{type(cost)}"
            )

        if nu is not None and not isinstance(nu, (int, float)):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR, f"nu 只支持(int,float)类型参数, 传入类型为{type(nu)}"
            )

        if terminationEpsilon is not None and not isinstance(
            terminationEpsilon, (int, float)
        ):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"terminationEpsilon 只支持(int,float)类型参数, 传入类型为{type(terminationEpsilon)}",
            )

        if lossEpsilon is not None and not isinstance(lossEpsilon, (int, float)):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"lossEpsilon 只支持(int,float)类型参数, 传入类型为{type(lossEpsilon)}",
            )

        invoke_args = {
            "svmType": svmType,
            "kernelType": kernelType,
            "shrinking": shrinking,
            "degree": degree,
            "gamma": gamma,
            "coef0": coef0,
            "cost": cost,
            "nu": nu,
            "terminationEpsilon": terminationEpsilon,
            "lossEpsilon": lossEpsilon,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        return FunctionHelper.apply("Classifier.libsvm", "aie.Classifier", invoke_args)

    @staticmethod
    def decisionTree(
        maxDepth: int = 5,
        maxNodes: int = None,
        minLeafPopulation: int = 5,
        minWeightFraction: [int, float] = 0.0,
        minInfoGain: [int, float] = 0.0,
        seed: int = 0,
    ) -> aie.Classifier:
        if maxDepth is not None and not isinstance(maxDepth, int):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR, f"maxDepth 只支持int类型参数, 传入类型为{type(maxDepth)}"
            )

        if maxNodes is not None and not isinstance(maxNodes, int):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR, f"maxNodes 只支持int类型参数, 传入类型为{type(maxNodes)}"
            )

        if minLeafPopulation is not None and not isinstance(minLeafPopulation, int):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"minLeafPopulation 只支持int类型参数, 传入类型为{type(minLeafPopulation)}",
            )

        if minWeightFraction is not None and not isinstance(
            minWeightFraction, (int, float)
        ):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"minWeightFraction 只支持(int,float)类型参数, 传入类型为{type(minWeightFraction)}",
            )

        if minInfoGain is not None and not isinstance(minInfoGain, (int, float)):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"minInfoGain 只支持(int,float)类型参数, 传入类型为{type(minInfoGain)}",
            )

        if seed is not None and not isinstance(seed, int):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR, f"seed 只支持int类型参数, 传入类型为{type(seed)}"
            )

        invoke_args = {
            "maxDepth": maxDepth,
            "maxNodes": maxNodes,
            "minLeafPopulation": minLeafPopulation,
            "minWeightFraction": minWeightFraction,
            "minInfoGain": minInfoGain,
            "seed": seed,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        return FunctionHelper.apply(
            "Classifier.decisionTree", "aie.Classifier", invoke_args
        )

    @staticmethod
    def cart(
        maxNodes: int = None, maxDepth: int = 20, minLeafPopulation: int = 5
    ) -> aie.Classifier:
        if maxNodes is not None and not isinstance(maxNodes, int):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR, f"maxNodes 只支持int类型参数, 传入类型为{type(maxNodes)}"
            )

        if maxDepth is not None and not isinstance(maxDepth, int):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR, f"maxDepth 只支持int类型参数, 传入类型为{type(maxDepth)}"
            )

        if minLeafPopulation is not None and not isinstance(minLeafPopulation, int):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"minLeafPopulation 只支持int类型参数, 传入类型为{type(minLeafPopulation)}",
            )

        invoke_args = {
            "maxNodes": maxNodes,
            "maxDepth": maxDepth,
            "minLeafPopulation": minLeafPopulation,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        return FunctionHelper.apply("Classifier.cart", "aie.Classifier", invoke_args)

    @staticmethod
    def randomForest(
        numTrees: int,
        maxDepth: int = 5,
        minLeafPopulation: int = 5,
        subsamplingRate: [int, float] = 1.0,
        seed: int = 0,
    ) -> aie.Classifier:
        if numTrees is not None and not isinstance(numTrees, int):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR, f"numTrees 只支持int类型参数, 传入类型为{type(numTrees)}"
            )

        if maxDepth is not None and not isinstance(maxDepth, int):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR, f"maxDepth 只支持int类型参数, 传入类型为{type(maxDepth)}"
            )

        if minLeafPopulation is not None and not isinstance(minLeafPopulation, int):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"minLeafPopulation 只支持int类型参数, 传入类型为{type(minLeafPopulation)}",
            )

        if subsamplingRate is not None and not isinstance(
            subsamplingRate, (int, float)
        ):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"subsamplingRate 只支持(int,float)类型参数, 传入类型为{type(subsamplingRate)}",
            )

        if seed is not None and not isinstance(seed, int):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR, f"seed 只支持int类型参数, 传入类型为{type(seed)}"
            )

        invoke_args = {
            "numTrees": numTrees,
            "maxDepth": maxDepth,
            "minLeafPopulation": minLeafPopulation,
            "subsamplingRate": subsamplingRate,
            "seed": seed,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        if "numTrees" not in invoke_args:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "参数numTrees不能为空")

        return FunctionHelper.apply(
            "Classifier.randomForest", "aie.Classifier", invoke_args
        )

    @staticmethod
    def gradientTreeBoost(
        numTrees: int,
        shrinkage: [int, float] = 0.005,
        samplingRate: [int, float] = 0.7,
        maxDepth: int = 20,
        maxNodes: int = None,
        minLeafPopulation: int = 5,
    ) -> aie.Classifier:
        if numTrees is not None and not isinstance(numTrees, int):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR, f"numTrees 只支持int类型参数, 传入类型为{type(numTrees)}"
            )

        if shrinkage is not None and not isinstance(shrinkage, (int, float)):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"shrinkage 只支持(int,float)类型参数, 传入类型为{type(shrinkage)}",
            )

        if samplingRate is not None and not isinstance(samplingRate, (int, float)):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"samplingRate 只支持(int,float)类型参数, 传入类型为{type(samplingRate)}",
            )

        if maxDepth is not None and not isinstance(maxDepth, int):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR, f"maxDepth 只支持int类型参数, 传入类型为{type(maxDepth)}"
            )

        if maxNodes is not None and not isinstance(maxNodes, int):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR, f"maxNodes 只支持int类型参数, 传入类型为{type(maxNodes)}"
            )

        if minLeafPopulation is not None and not isinstance(minLeafPopulation, int):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"minLeafPopulation 只支持int类型参数, 传入类型为{type(minLeafPopulation)}",
            )

        invoke_args = {
            "numTrees": numTrees,
            "shrinkage": shrinkage,
            "samplingRate": samplingRate,
            "maxDepth": maxDepth,
            "maxNodes": maxNodes,
            "minLeafPopulation": minLeafPopulation,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        if "numTrees" not in invoke_args:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "参数numTrees不能为空")

        return FunctionHelper.apply(
            "Classifier.gradientTreeBoost", "aie.Classifier", invoke_args
        )

    @staticmethod
    def adaBoost(
        numTrees: int,
        maxDepth: int = 20,
        maxNodes: int = None,
        minLeafPopulation: int = 5,
    ) -> aie.Classifier:
        if numTrees is not None and not isinstance(numTrees, int):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR, f"numTrees 只支持int类型参数, 传入类型为{type(numTrees)}"
            )

        if maxDepth is not None and not isinstance(maxDepth, int):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR, f"maxDepth 只支持int类型参数, 传入类型为{type(maxDepth)}"
            )

        if maxNodes is not None and not isinstance(maxNodes, int):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR, f"maxNodes 只支持int类型参数, 传入类型为{type(maxNodes)}"
            )

        if minLeafPopulation is not None and not isinstance(minLeafPopulation, int):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"minLeafPopulation 只支持int类型参数, 传入类型为{type(minLeafPopulation)}",
            )

        invoke_args = {
            "numTrees": numTrees,
            "maxDepth": maxDepth,
            "maxNodes": maxNodes,
            "minLeafPopulation": minLeafPopulation,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        if "numTrees" not in invoke_args:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "参数numTrees不能为空")

        return FunctionHelper.apply(
            "Classifier.adaBoost", "aie.Classifier", invoke_args
        )

    @staticmethod
    def naiveBayes(smooth: [int, float] = 1.0) -> aie.Classifier:
        if smooth is not None and not isinstance(smooth, (int, float)):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"smooth 只支持(int,float)类型参数, 传入类型为{type(smooth)}",
            )

        invoke_args = {
            "smooth": smooth,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        return FunctionHelper.apply(
            "Classifier.naiveBayes", "aie.Classifier", invoke_args
        )

    def confusionMatrix(self) -> aie.ConfusionMatrix:
        invoke_args = {
            "input": self,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        return FunctionHelper.apply(
            "Classifier.confusionMatrix", "aie.ConfusionMatrix", invoke_args
        )
