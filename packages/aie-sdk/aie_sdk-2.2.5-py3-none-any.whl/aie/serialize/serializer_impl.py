#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .gen_visitor import GenVisitor
import json
from .optimizer import Optimizer


class Serializer(object):
    def __init__(self):
        pass

    def encode(self, obj, is_compacted=True) -> str:
        visitor = GenVisitor(is_compacted)
        ref = visitor.visit(obj)
        optimizer = Optimizer(ref, visitor.scope, visitor.ref_uses_cnt)
        optimize_ref = optimizer.optimize()
        result = {"result": optimize_ref, "values": optimizer.optimized_values}

        # visitor = GenVisitor(False)
        # value = visitor.visit(obj)
        # result = {"result": 0, "values": {"0": value}}

        return json.dumps(result, ensure_ascii=False, allow_nan=False)
