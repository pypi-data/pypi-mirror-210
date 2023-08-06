#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from .function_node import FunctionNode
from . import aie_object
from .error.aie_error import AIEError, AIEErrorCode
import aie


class FunctionHelper(object):
    @classmethod
    def cast(cls, node, kclass):
        if kclass == "aie.Image":
            node.__class__ = aie.Image
        elif kclass == "aie.Collection":
            node.__class__ = aie.Collection
        elif kclass == "aie.ImageCollection":
            node.__class__ = aie.ImageCollection
        elif kclass == "aie.Geometry":
            node.__class__ = aie.Geometry
        elif kclass == "aie.Feature":
            node.__class__ = aie.Feature
        elif kclass == "aie.FeatureCollection":
            node.__class__ = aie.FeatureCollection
        elif kclass == "aie.Filter":
            node.__class__ = aie.Filter
        elif kclass == "aie.Reducer":
            node.__class__ = aie.Reducer
        elif kclass == "aie.Terrain":
            node.__class__ = aie.Terrain
        elif kclass == "aie.Kernel":
            node.__class__ = aie.Kernel
        elif kclass == "aie.Classifier":
            node.__class__ = aie.Classifier
        elif kclass == "aie.ConfusionMatrix":
            node.__class__ = aie.ConfusionMatrix
        elif kclass in ("int", "float", "bool", "str", "list", "tuple", "dict", "object"):
            pass
        else:
            raise AIEError(AIEErrorCode.DEFAULT_INTERNAL_ERROR,
                           "", "FunctionHelper::cast kclass " + kclass + " not support")
        return node

    @classmethod
    def apply(cls, name, returns, args):
        node = FunctionNode(name, args)
        return cls.cast(node, returns)
