#!/usr/bin/env python
# -*- coding: utf-8 -*-

import aie
import collections


class GenVisitor(object):
    def __init__(self, is_compacted=True):
        self.is_compacted = is_compacted
        # {obj_id: ref}
        self.refs = {}
        # [(ref, value)]
        self.scope = []
        # {ref: use_count}
        self.ref_uses_cnt = collections.defaultdict(int)

    def visit(self, obj):
        obj_id = id(obj)
        if self.is_compacted:
            ref = self.refs.get(obj_id, None)
            if ref:
                self.ref_uses_cnt[ref] += 1
                return ref

        if isinstance(obj, aie.customfunction_node.CustomFunctionNode):
            result = {
                "functionDefinitionValue": {
                    "argumentNames": obj.arg_names,
                    "body": self.visit(obj.body)
                }
            }
        elif isinstance(obj, aie.function_node.FunctionNode):
            if obj._isVariable():
                result = {
                    "argumentReference": obj.var_name
                }
            else:
                args_dict = dict()
                for key in sorted(obj.invoke_args):
                    args_dict[key] = self.visit(obj.invoke_args[key])
                if self.is_compacted:
                    result = {
                        "functionInvocationValue": {
                            "functionName": obj.func_name,
                            "arguments": {k: {
                                "valueReference": v
                            } for k, v in args_dict.items()},
                        }
                    }
                else:
                    result = {
                        "functionInvocationValue": {
                            "functionName": obj.func_name,
                            "arguments": args_dict,
                        }
                    }
        elif isinstance(obj, (int, float, bool, str)):
            result = {"constantValue": obj}
        elif isinstance(obj, (list, tuple)):
            values = [self.visit(item) for item in obj]
            """ constant optimizer
            "arrayValue": {
                "values": [
                    {
                        "constantValue": "xx"
                    }
                ]
            }
            """
            if all("constantValue" in value for value in values):
                result = {
                    "constantValue": [value["constantValue"] for value in values]
                }
            else:
                if self.is_compacted:
                    result = {"arrayValue": {
                        "values": [{"valueReference": value} for value in values]
                    }}
                else:
                    result = {"arrayValue": {
                        "values": values
                    }}
        elif isinstance(obj, dict):
            values = {k: self.visit(obj[k]) for k in sorted(obj)}
            """ constant optimizer
            "dictionaryValue": {
                "values": {
                    "key1": {
                        "constantValue": "xx"
                    }
                }
            }
            """
            if all("constantValue" in value for value in values.values()):
                result = {
                    "constantValue": {key: value["constantValue"] for key, value in values.items()}
                }
            else:
                if self.is_compacted:
                    result = {
                        "dictionaryValue": {
                            "values": {
                                k: {
                                    "valueReference": v
                                } for k, v in values.items()
                            }
                        }
                    }
                else:
                    result = {
                        "dictionaryValue": {
                            "values": values
                        }
                    }
        else:
            raise aie.error.aie_error.AIEError(aie.error.aie_error.AIEErrorCode.DEFAULT_INTERNAL_ERROR,
                                               "", "serialize.GenVisitor.visit not support obj type %s" % type(
                                                   obj)
                                               )

        if self.is_compacted:
            ref = self.refs.get(obj_id, None)
            if not ref:
                ref = str(len(self.scope))
                self.scope.append((ref, result))
                self.refs[obj_id] = ref
            self.ref_uses_cnt[ref] += 1
            return ref
        else:
            return result
