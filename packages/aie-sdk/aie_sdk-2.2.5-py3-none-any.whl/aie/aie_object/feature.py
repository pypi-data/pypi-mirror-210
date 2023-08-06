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


class Feature(FunctionNode):
    def __init__(self, geometry, properties=None) -> aie.Feature:
        args = geometry
        if isinstance(args, aie.Geometry):
            if properties is not None and not isinstance(properties, dict):
                raise AIEError(
                    AIEErrorCode.ARGS_ERROR,
                    f"properties 只支持dict类型参数, 传入类型为{type(properties)}",
                )

            invoke_args = {
                "geometry": geometry,
                "properties": properties,
            }

            invoke_args = {k: v for k, v in invoke_args.items() if v is not None}
            super(Feature, self).__init__("Feature", invoke_args)
        elif isinstance(args, aie.variable_node.VariableNode):
            super(Feature, self).__init__(
                args.func_name, args.invoke_args, args.var_name
            )
        elif isinstance(args, aie.function_node.FunctionNode):
            super(Feature, self).__init__(
                args.func_name, args.invoke_args, args.var_name
            )
        elif args is None:
            invoke_args = {
                "geometry": geometry,
                "properties": properties,
            }

            invoke_args = {k: v for k, v in invoke_args.items() if v is not None}
            super(Feature, self).__init__("Feature", invoke_args)
        else:
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"geometry 只支持aie.Geometry类型参数, 传入类型为{type(geometry)}",
            )

    def getMapId(self, vis_params):
        if vis_params is not None and not isinstance(vis_params, dict):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"vis_params 只支持dict类型参数, 传入类型为{type(vis_params)}",
            )
        return aie.client.Maps.getMapId(self, vis_params)

    def getCenter(self) -> tuple:
        bbox = aie.client.InteractiveSession.getBounds(self)
        if bbox is not None and isinstance(bbox, list):
            center = ((bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2)
            return center
        raise AIEError(AIEErrorCode.ARGS_ERROR, f"获取Center失败. bbox: {bbox}")

    def getBounds(self) -> list:
        bbox = aie.client.InteractiveSession.getBounds(self)
        if bbox is not None and isinstance(bbox, list):
            bounds = [bbox[0], bbox[1], bbox[2], bbox[3]]
            return bounds
        raise AIEError(AIEErrorCode.ARGS_ERROR, f"获取Bounds失败. bbox: {bbox}")

    def get(self, property: str) -> object:
        if property is not None and not isinstance(property, str):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR, f"property 只支持str类型参数, 传入类型为{type(property)}"
            )

        invoke_args = {
            "input": self,
            "property": property,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        if "property" not in invoke_args:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "参数property不能为空")

        return FunctionHelper.apply("Feature.get", "object", invoke_args)

    def propertyNames(self) -> object:
        invoke_args = {
            "element": self,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        return FunctionHelper.apply("Feature.propertyNames", "object", invoke_args)

    def select(
        self,
        propertySelectors: list,
        newProperties: list = None,
        retainGeometry: bool = True,
    ) -> object:
        if propertySelectors is not None and not isinstance(propertySelectors, list):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"propertySelectors 只支持list类型参数, 传入类型为{type(propertySelectors)}",
            )

        if newProperties is not None and not isinstance(newProperties, list):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"newProperties 只支持list类型参数, 传入类型为{type(newProperties)}",
            )

        if retainGeometry is not None and not isinstance(retainGeometry, bool):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"retainGeometry 只支持bool类型参数, 传入类型为{type(retainGeometry)}",
            )

        invoke_args = {
            "input": self,
            "propertySelectors": propertySelectors,
            "newProperties": newProperties,
            "retainGeometry": retainGeometry,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        if "propertySelectors" not in invoke_args:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "参数propertySelectors不能为空")

        return FunctionHelper.apply("Feature.select", "object", invoke_args)

    def toArray(self, properties: list) -> object:
        if properties is not None and not isinstance(properties, list):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"properties 只支持list类型参数, 传入类型为{type(properties)}",
            )

        invoke_args = {
            "feature": self,
            "properties": properties,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        if "properties" not in invoke_args:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "参数properties不能为空")

        return FunctionHelper.apply("Feature.toArray", "object", invoke_args)

    def toDictionary(self, properties: list = None) -> object:
        if properties is not None and not isinstance(properties, list):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"properties 只支持list类型参数, 传入类型为{type(properties)}",
            )

        invoke_args = {
            "element": self,
            "properties": properties,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        return FunctionHelper.apply("Feature.toDictionary", "object", invoke_args)

    def set(self, var_args: dict) -> aie.Feature:
        if var_args is not None and not isinstance(var_args, dict):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR, f"var_args 只支持dict类型参数, 传入类型为{type(var_args)}"
            )

        invoke_args = {
            "element": self,
            "var_args": var_args,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        if "var_args" not in invoke_args:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "参数var_args不能为空")

        return FunctionHelper.apply("Feature.set", "aie.Feature", invoke_args)

    def setGeometry(self, geometry: aie.Geometry) -> aie.Feature:
        if geometry is not None and not isinstance(geometry, aie.Geometry):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"geometry 只支持aie.Geometry类型参数, 传入类型为{type(geometry)}",
            )

        invoke_args = {
            "feature": self,
            "geometry": geometry,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        if "geometry" not in invoke_args:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "参数geometry不能为空")

        return FunctionHelper.apply("Feature.setGeometry", "aie.Feature", invoke_args)

    def area(self) -> object:
        invoke_args = {
            "feature": self,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        return FunctionHelper.apply("Feature.area", "object", invoke_args)

    def perimeter(self) -> object:
        invoke_args = {
            "feature": self,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        return FunctionHelper.apply("Feature.perimeter", "object", invoke_args)

    def length(self) -> object:
        invoke_args = {
            "feature": self,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        return FunctionHelper.apply("Feature.length", "object", invoke_args)

    def bounds(self) -> aie.Feature:
        invoke_args = {
            "feature": self,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        return FunctionHelper.apply("Feature.bounds", "aie.Feature", invoke_args)

    def centroid(self) -> aie.Feature:
        invoke_args = {
            "feature": self,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        return FunctionHelper.apply("Feature.centroid", "aie.Feature", invoke_args)

    def convexHull(self) -> aie.Feature:
        invoke_args = {
            "feature": self,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        return FunctionHelper.apply("Feature.convexHull", "aie.Feature", invoke_args)

    def cutLines(self, distances: list) -> aie.Feature:
        if distances is not None and not isinstance(distances, list):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"distances 只支持list类型参数, 传入类型为{type(distances)}",
            )

        invoke_args = {
            "feature": self,
            "distances": distances,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        if "distances" not in invoke_args:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "参数distances不能为空")

        return FunctionHelper.apply("Feature.cutLines", "aie.Feature", invoke_args)

    def simplify(self, tolerance: [int, float]) -> aie.Feature:
        if tolerance is not None and not isinstance(tolerance, (int, float)):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"tolerance 只支持(int,float)类型参数, 传入类型为{type(tolerance)}",
            )

        invoke_args = {
            "feature": self,
            "tolerance": tolerance,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        if "tolerance" not in invoke_args:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "参数tolerance不能为空")

        return FunctionHelper.apply("Feature.simplify", "aie.Feature", invoke_args)

    def transform(self, proj: str) -> aie.Feature:
        if proj is not None and not isinstance(proj, str):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR, f"proj 只支持str类型参数, 传入类型为{type(proj)}"
            )

        invoke_args = {
            "feature": self,
            "proj": proj,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        if "proj" not in invoke_args:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "参数proj不能为空")

        return FunctionHelper.apply("Feature.transform", "aie.Feature", invoke_args)

    def containedIn(self, right: aie.Feature) -> object:
        if right is not None and not isinstance(right, aie.Feature):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR, f"right 只支持aie.Feature类型参数, 传入类型为{type(right)}"
            )

        invoke_args = {
            "left": self,
            "right": right,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        if "right" not in invoke_args:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "参数right不能为空")

        return FunctionHelper.apply("Feature.containedIn", "object", invoke_args)

    def contains(self, right: aie.Feature) -> object:
        if right is not None and not isinstance(right, aie.Feature):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR, f"right 只支持aie.Feature类型参数, 传入类型为{type(right)}"
            )

        invoke_args = {
            "left": self,
            "right": right,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        if "right" not in invoke_args:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "参数right不能为空")

        return FunctionHelper.apply("Feature.contains", "object", invoke_args)

    def difference(self, right: aie.Feature) -> aie.Feature:
        if right is not None and not isinstance(right, aie.Feature):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR, f"right 只支持aie.Feature类型参数, 传入类型为{type(right)}"
            )

        invoke_args = {
            "left": self,
            "right": right,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        if "right" not in invoke_args:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "参数right不能为空")

        return FunctionHelper.apply("Feature.difference", "aie.Feature", invoke_args)

    def disjoint(self, right: aie.Feature) -> object:
        if right is not None and not isinstance(right, aie.Feature):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR, f"right 只支持aie.Feature类型参数, 传入类型为{type(right)}"
            )

        invoke_args = {
            "left": self,
            "right": right,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        if "right" not in invoke_args:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "参数right不能为空")

        return FunctionHelper.apply("Feature.disjoint", "object", invoke_args)

    def dissolve(self) -> aie.Feature:
        invoke_args = {
            "feature": self,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        return FunctionHelper.apply("Feature.dissolve", "aie.Feature", invoke_args)

    def distance(self, right: aie.Feature) -> object:
        if right is not None and not isinstance(right, aie.Feature):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR, f"right 只支持aie.Feature类型参数, 传入类型为{type(right)}"
            )

        invoke_args = {
            "left": self,
            "right": right,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        if "right" not in invoke_args:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "参数right不能为空")

        return FunctionHelper.apply("Feature.distance", "object", invoke_args)

    def withinDistance(self, right: aie.Feature, distance: [int, float]) -> object:
        if right is not None and not isinstance(right, aie.Feature):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR, f"right 只支持aie.Feature类型参数, 传入类型为{type(right)}"
            )

        if distance is not None and not isinstance(distance, (int, float)):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"distance 只支持(int,float)类型参数, 传入类型为{type(distance)}",
            )

        invoke_args = {
            "left": self,
            "right": right,
            "distance": distance,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        if "right" not in invoke_args:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "参数right不能为空")

        if "distance" not in invoke_args:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "参数distance不能为空")

        return FunctionHelper.apply("Feature.withinDistance", "object", invoke_args)

    def intersection(self, right: aie.Feature) -> aie.Feature:
        if right is not None and not isinstance(right, aie.Feature):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR, f"right 只支持aie.Feature类型参数, 传入类型为{type(right)}"
            )

        invoke_args = {
            "left": self,
            "right": right,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        if "right" not in invoke_args:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "参数right不能为空")

        return FunctionHelper.apply("Feature.intersection", "aie.Feature", invoke_args)

    def intersects(self, right: aie.Feature) -> object:
        if right is not None and not isinstance(right, aie.Feature):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR, f"right 只支持aie.Feature类型参数, 传入类型为{type(right)}"
            )

        invoke_args = {
            "left": self,
            "right": right,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        if "right" not in invoke_args:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "参数right不能为空")

        return FunctionHelper.apply("Feature.intersects", "object", invoke_args)

    def symmetricDifference(self, right: aie.Feature) -> aie.Feature:
        if right is not None and not isinstance(right, aie.Feature):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR, f"right 只支持aie.Feature类型参数, 传入类型为{type(right)}"
            )

        invoke_args = {
            "left": self,
            "right": right,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        if "right" not in invoke_args:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "参数right不能为空")

        return FunctionHelper.apply(
            "Feature.symmetricDifference", "aie.Feature", invoke_args
        )

    def union(self, right: aie.Feature) -> aie.Feature:
        if right is not None and not isinstance(right, aie.Feature):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR, f"right 只支持aie.Feature类型参数, 传入类型为{type(right)}"
            )

        invoke_args = {
            "left": self,
            "right": right,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        if "right" not in invoke_args:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "参数right不能为空")

        return FunctionHelper.apply("Feature.union", "aie.Feature", invoke_args)

    def buffer(self, distance: [int, float]) -> aie.Feature:
        if distance is not None and not isinstance(distance, (int, float)):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"distance 只支持(int,float)类型参数, 传入类型为{type(distance)}",
            )

        invoke_args = {
            "feature": self,
            "distance": distance,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        if "distance" not in invoke_args:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "参数distance不能为空")

        return FunctionHelper.apply("Feature.buffer", "aie.Feature", invoke_args)

    def copyProperties(
        self, source: aie.Feature, properties: list = None, exclude: list = None
    ) -> aie.Feature:
        if source is not None and not isinstance(source, aie.Feature):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"source 只支持aie.Feature类型参数, 传入类型为{type(source)}",
            )

        if properties is not None and not isinstance(properties, list):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"properties 只支持list类型参数, 传入类型为{type(properties)}",
            )

        if exclude is not None and not isinstance(exclude, list):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR, f"exclude 只支持list类型参数, 传入类型为{type(exclude)}"
            )

        invoke_args = {
            "destination": self,
            "source": source,
            "properties": properties,
            "exclude": exclude,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        if "source" not in invoke_args:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "参数source不能为空")

        return FunctionHelper.apply(
            "Feature.copyProperties", "aie.Feature", invoke_args
        )

    def voronoiDiagram(self) -> aie.Feature:
        invoke_args = {
            "feature": self,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        return FunctionHelper.apply(
            "Feature.voronoiDiagram", "aie.Feature", invoke_args
        )

    def delaunayTriangulation(self) -> aie.Feature:
        invoke_args = {
            "feature": self,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        return FunctionHelper.apply(
            "Feature.delaunayTriangulation", "aie.Feature", invoke_args
        )

    def smooth(
        self, iterations: int, offset: [int, float], maxAngle: [int, float]
    ) -> aie.Feature:
        if iterations is not None and not isinstance(iterations, int):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"iterations 只支持int类型参数, 传入类型为{type(iterations)}",
            )

        if offset is not None and not isinstance(offset, (int, float)):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"offset 只支持(int,float)类型参数, 传入类型为{type(offset)}",
            )

        if maxAngle is not None and not isinstance(maxAngle, (int, float)):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"maxAngle 只支持(int,float)类型参数, 传入类型为{type(maxAngle)}",
            )

        invoke_args = {
            "feature": self,
            "iterations": iterations,
            "offset": offset,
            "maxAngle": maxAngle,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        if "iterations" not in invoke_args:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "参数iterations不能为空")

        if "offset" not in invoke_args:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "参数offset不能为空")

        if "maxAngle" not in invoke_args:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "参数maxAngle不能为空")

        return FunctionHelper.apply("Feature.smooth", "aie.Feature", invoke_args)

    def getNumber(self, property: str) -> object:
        if property is not None and not isinstance(property, str):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR, f"property 只支持str类型参数, 传入类型为{type(property)}"
            )

        invoke_args = {
            "input": self,
            "property": property,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        if "property" not in invoke_args:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "参数property不能为空")

        return FunctionHelper.apply("Feature.getNumber", "object", invoke_args)

    def getString(self, property: str) -> object:
        if property is not None and not isinstance(property, str):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR, f"property 只支持str类型参数, 传入类型为{type(property)}"
            )

        invoke_args = {
            "input": self,
            "property": property,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        if "property" not in invoke_args:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "参数property不能为空")

        return FunctionHelper.apply("Feature.getString", "object", invoke_args)

    def renamePropertyNames(self, var_args: dict) -> aie.Feature:
        if var_args is not None and not isinstance(var_args, dict):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR, f"var_args 只支持dict类型参数, 传入类型为{type(var_args)}"
            )

        invoke_args = {
            "input": self,
            "var_args": var_args,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        if "var_args" not in invoke_args:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "参数var_args不能为空")

        return FunctionHelper.apply(
            "Feature.renamePropertyNames", "aie.Feature", invoke_args
        )
