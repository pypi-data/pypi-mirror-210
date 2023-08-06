#!/usr/bin/env python
# -*- coding: utf-8 -*-

import aie
from aie.error import AIEError, AIEErrorCode


class Optimizer(object):
    def __init__(self, result, values, use_count):
        # ref
        self.result = result
        # [(ref, value)]
        self.values = values
        # {ref: use_count}
        self.use_count = use_count

        # {ref: optimized_ref}
        self.optimized_ref_map = {}
        # {ref: value}
        self.optimized_values = {}

    def optimize(self):
        optimized_result = self.optimize_referred_value(self.result)
        return optimized_result

    def optimize_value(self, value):
        if any(x in value for x in ["constantValue", "argumentReference"]):
            return value
        elif "arrayValue" in value:
            node = value["arrayValue"]
            optimized_value = [self.optimize_value(v) for v in node["values"]]

            if all("constantValue" in value for value in optimized_value):
                return {
                    "constantValue": [value["constantValue"] for value in optimized_value]
                }
            else:
                return {"arrayValue": {"values": optimized_value}}
        elif "dictionaryValue" in value:
            node = value["dictionaryValue"]
            optimized_value = {k: self.optimize_value(
                v) for k, v in node["values"].items()}
            if all("constantValue" in value for value in optimized_value.values()):
                return {
                    "constantValue": {key: value["constantValue"] for key, value in optimized_value.items()}
                }
            else:
                return {"dictionaryValue": {"values": optimized_value}}
        elif "functionInvocationValue" in value:
            node = value["functionInvocationValue"]

            optimized_value = {}
            optimized_value["functionName"] = node["functionName"]
            optimized_value["arguments"] = {k: self.optimize_value(
                v)for k, v in node["arguments"].items()}
            return {"functionInvocationValue": optimized_value}
        elif "valueReference" in value:
            ref = value["valueReference"]
            if self.use_count[ref] == 1:
                referenced_value = self.values[int(ref)][1]
                return self.optimize_value(referenced_value)
            else:
                return {"valueReference": self.optimize_referred_value(ref)}
        elif "functionDefinitionValue" in value:
            node = value["functionDefinitionValue"]

            optimized_value = {}
            optimized_value["argumentNames"] = node["argumentNames"]
            optimized_value["body"] = self.optimize_referred_value(
                node["body"])
            return {
                "functionDefinitionValue": optimized_value
            }
        else:
            raise AIEError(AIEErrorCode.DEFAULT_INTERNAL_ERROR, "",
                           f"optimize不支持value: {value}")

    def optimize_referred_value(self, reference):
        if reference in self.optimized_ref_map:
            return self.optimized_ref_map[reference]
        optimized_ref = str(len(self.optimized_ref_map))
        self.optimized_ref_map[reference] = optimized_ref
        self.optimized_values[optimized_ref] = self.optimize_value(
            self.values[int(reference)][1])
        return optimized_ref
