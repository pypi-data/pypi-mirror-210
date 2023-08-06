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


class ImageCollection(aie.Collection):
    def __init__(self, args) -> aie.ImageCollection:
        if isinstance(args, str):
            invoke_args = {"id": args}
            super(ImageCollection, self).__init__("ImageCollection.load", invoke_args)
        elif isinstance(args, aie.Image):
            args = [args]
            invoke_args = {"images": args}
            super(ImageCollection, self).__init__(
                "ImageCollection.fromImages", invoke_args
            )
        elif isinstance(args, (list, tuple)):
            images = [aie.Image(i) for i in args]
            invoke_args = {"images": images}
            super(ImageCollection, self).__init__(
                "ImageCollection.fromImages", invoke_args
            )
        else:
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"args 只支持str|aie.Image|list类型参数, 传入类型为{type(args)}",
            )

    def elementType(self):
        return aie.Image

    def getMapId(self, vis_params):
        if vis_params is not None and not isinstance(vis_params, dict):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"vis_params 只支持dict类型参数, 传入类型为{type(vis_params)}",
            )
        return aie.client.Maps.getMapId(self, vis_params)

    def mosaic(self) -> aie.Image:
        invoke_args = {
            "collection": self,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        return FunctionHelper.apply("ImageCollection.mosaic", "aie.Image", invoke_args)

    def qualityMosaic(self, qualityBand: str) -> aie.Image:
        if qualityBand is not None and not isinstance(qualityBand, str):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"qualityBand 只支持str类型参数, 传入类型为{type(qualityBand)}",
            )

        invoke_args = {
            "collection": self,
            "qualityBand": qualityBand,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        if "qualityBand" not in invoke_args:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "参数qualityBand不能为空")

        return FunctionHelper.apply(
            "ImageCollection.qualityMosaic", "aie.Image", invoke_args
        )

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

    def toList(self, count: int, offset: int = 0) -> object:
        if count is not None and not isinstance(count, int):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR, f"count 只支持int类型参数, 传入类型为{type(count)}"
            )

        if offset is not None and not isinstance(offset, int):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR, f"offset 只支持int类型参数, 传入类型为{type(offset)}"
            )

        invoke_args = {
            "collection": self,
            "count": count,
            "offset": offset,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        if "count" not in invoke_args:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "参数count不能为空")

        return FunctionHelper.apply("ImageCollection.toList", "object", invoke_args)

    def filter(self, filter: Union[str, aie.Filter]) -> aie.ImageCollection:
        node = super(ImageCollection, self).filter(filter)
        return FunctionHelper.cast(node, "aie.ImageCollection")

    def filterBounds(
        self, geometry: Union[aie.Geometry, aie.Feature, aie.FeatureCollection]
    ) -> aie.ImageCollection:
        node = super(ImageCollection, self).filterBounds(geometry)
        return FunctionHelper.cast(node, "aie.ImageCollection")

    def filterDate(self, start: str, end: str) -> aie.ImageCollection:
        if start is not None and not isinstance(start, str):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR, f"start 只支持str类型参数, 传入类型为{type(start)}"
            )

        if end is not None and not isinstance(end, str):
            raise AIEError(AIEErrorCode.ARGS_ERROR, f"end 只支持str类型参数, 传入类型为{type(end)}")

        invoke_args = {
            "collection": self,
            "start": start,
            "end": end,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        if "start" not in invoke_args:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "参数start不能为空")

        if "end" not in invoke_args:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "参数end不能为空")

        return FunctionHelper.apply(
            "Collection.filterDate", "aie.ImageCollection", invoke_args
        )

    def first(self) -> aie.Image:
        node = super(ImageCollection, self).first()
        return FunctionHelper.cast(node, "aie.Image")

    def limit(
        self, limit: int, property: str = None, ascending: bool = True
    ) -> aie.ImageCollection:
        node = super(ImageCollection, self).limit(limit, property=None, ascending=True)
        return FunctionHelper.cast(node, "aie.ImageCollection")

    def reduce(self, reducer: aie.Reducer) -> aie.Image:
        if reducer is not None and not isinstance(reducer, aie.Reducer):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"reducer 只支持aie.Reducer类型参数, 传入类型为{type(reducer)}",
            )

        invoke_args = {
            "collection": self,
            "reducer": reducer,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        if "reducer" not in invoke_args:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "参数reducer不能为空")

        return FunctionHelper.apply("ImageCollection.reduce", "aie.Image", invoke_args)

    def And(self) -> aie.Image:
        invoke_args = {
            "collection": self,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        return FunctionHelper.apply("reduce.and", "aie.Image", invoke_args)

    def count(self) -> aie.Image:
        invoke_args = {
            "collection": self,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        return FunctionHelper.apply("reduce.count", "aie.Image", invoke_args)

    def max(self) -> aie.Image:
        invoke_args = {
            "collection": self,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        return FunctionHelper.apply("reduce.max", "aie.Image", invoke_args)

    def mean(self) -> aie.Image:
        invoke_args = {
            "collection": self,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        return FunctionHelper.apply("reduce.mean", "aie.Image", invoke_args)

    def median(self) -> aie.Image:
        invoke_args = {
            "collection": self,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        return FunctionHelper.apply("reduce.median", "aie.Image", invoke_args)

    def min(self) -> aie.Image:
        invoke_args = {
            "collection": self,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        return FunctionHelper.apply("reduce.min", "aie.Image", invoke_args)

    def mode(self) -> aie.Image:
        invoke_args = {
            "collection": self,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        return FunctionHelper.apply("reduce.mode", "aie.Image", invoke_args)

    def Or(self) -> aie.Image:
        invoke_args = {
            "collection": self,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        return FunctionHelper.apply("reduce.or", "aie.Image", invoke_args)

    def product(self) -> aie.Image:
        invoke_args = {
            "collection": self,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        return FunctionHelper.apply("reduce.product", "aie.Image", invoke_args)

    def sum(self) -> aie.Image:
        invoke_args = {
            "collection": self,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        return FunctionHelper.apply("reduce.sum", "aie.Image", invoke_args)

    def map(
        self, baseAlgorithm: types.FunctionType
    ) -> Union[aie.ImageCollection, aie.FeatureCollection]:
        node = super(ImageCollection, self).map(baseAlgorithm)
        baseAlgorithm_return_type = type(node.invoke_args["baseAlgorithm"].body)
        if aie.Feature == baseAlgorithm_return_type:
            return FunctionHelper.cast(node, "aie.FeatureCollection")
        else:
            return FunctionHelper.cast(node, "aie.ImageCollection")

    def select(self, selectors) -> aie.ImageCollection:
        return self.map(lambda image: image.select(selectors))

    def sort(self, property: str, ascending: bool = True) -> aie.ImageCollection:
        if property is not None and not isinstance(property, str):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR, f"property 只支持str类型参数, 传入类型为{type(property)}"
            )

        if ascending is not None and not isinstance(ascending, bool):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"ascending 只支持bool类型参数, 传入类型为{type(ascending)}",
            )

        invoke_args = {
            "collection": self,
            "property": property,
            "ascending": ascending,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        if "property" not in invoke_args:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "参数property不能为空")

        return FunctionHelper.apply(
            "ImageCollection.sort", "aie.ImageCollection", invoke_args
        )

    def toBands(self) -> aie.Image:
        invoke_args = {
            "collection": self,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        return FunctionHelper.apply("ImageCollection.toBands", "aie.Image", invoke_args)

    @staticmethod
    def fromImages(images: list) -> aie.ImageCollection:
        if images is not None and not isinstance(images, list):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR, f"images 只支持list类型参数, 传入类型为{type(images)}"
            )

        invoke_args = {
            "images": images,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        if "images" not in invoke_args:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "参数images不能为空")

        return FunctionHelper.apply(
            "ImageCollection.fromImages", "aie.ImageCollection", invoke_args
        )

    def merge(self, collection2: aie.ImageCollection) -> aie.ImageCollection:
        if collection2 is not None and not isinstance(collection2, aie.ImageCollection):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"collection2 只支持aie.ImageCollection类型参数, 传入类型为{type(collection2)}",
            )

        invoke_args = {
            "input": self,
            "collection2": collection2,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        if "collection2" not in invoke_args:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "参数collection2不能为空")

        return FunctionHelper.apply(
            "ImageCollection.merge", "aie.ImageCollection", invoke_args
        )

    def cast(self, bandTypes: dict) -> aie.ImageCollection:
        if bandTypes is not None and not isinstance(bandTypes, dict):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR,
                f"bandTypes 只支持dict类型参数, 传入类型为{type(bandTypes)}",
            )

        invoke_args = {
            "input": self,
            "bandTypes": bandTypes,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        if "bandTypes" not in invoke_args:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "参数bandTypes不能为空")

        return FunctionHelper.apply(
            "ImageCollection.cast", "aie.ImageCollection", invoke_args
        )

    def aggregate_max(self, property: str) -> object:
        if property is not None and not isinstance(property, str):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR, f"property 只支持str类型参数, 传入类型为{type(property)}"
            )

        invoke_args = {
            "collection": self,
            "property": property,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        if "property" not in invoke_args:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "参数property不能为空")

        return FunctionHelper.apply(
            "ImageCollection.aggregate_max", "object", invoke_args
        )

    def aggregate_min(self, property: str) -> object:
        if property is not None and not isinstance(property, str):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR, f"property 只支持str类型参数, 传入类型为{type(property)}"
            )

        invoke_args = {
            "collection": self,
            "property": property,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        if "property" not in invoke_args:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "参数property不能为空")

        return FunctionHelper.apply(
            "ImageCollection.aggregate_min", "object", invoke_args
        )

    def aggregate_mean(self, property: str) -> object:
        if property is not None and not isinstance(property, str):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR, f"property 只支持str类型参数, 传入类型为{type(property)}"
            )

        invoke_args = {
            "collection": self,
            "property": property,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        if "property" not in invoke_args:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "参数property不能为空")

        return FunctionHelper.apply(
            "ImageCollection.aggregate_mean", "object", invoke_args
        )

    def aggregate_count(self, property: str) -> object:
        if property is not None and not isinstance(property, str):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR, f"property 只支持str类型参数, 传入类型为{type(property)}"
            )

        invoke_args = {
            "collection": self,
            "property": property,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        if "property" not in invoke_args:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "参数property不能为空")

        return FunctionHelper.apply(
            "ImageCollection.aggregate_count", "object", invoke_args
        )

    def aggregate_sum(self, property: str) -> object:
        if property is not None and not isinstance(property, str):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR, f"property 只支持str类型参数, 传入类型为{type(property)}"
            )

        invoke_args = {
            "collection": self,
            "property": property,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        if "property" not in invoke_args:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "参数property不能为空")

        return FunctionHelper.apply(
            "ImageCollection.aggregate_sum", "object", invoke_args
        )

    def aggregate_stats(self, property: str) -> object:
        if property is not None and not isinstance(property, str):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR, f"property 只支持str类型参数, 传入类型为{type(property)}"
            )

        invoke_args = {
            "collection": self,
            "property": property,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        if "property" not in invoke_args:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "参数property不能为空")

        return FunctionHelper.apply(
            "ImageCollection.aggregate_stats", "object", invoke_args
        )

    def aggregate_array(self, property: str) -> object:
        if property is not None and not isinstance(property, str):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR, f"property 只支持str类型参数, 传入类型为{type(property)}"
            )

        invoke_args = {
            "collection": self,
            "property": property,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        if "property" not in invoke_args:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "参数property不能为空")

        return FunctionHelper.apply(
            "ImageCollection.aggregate_array", "object", invoke_args
        )

    def aggregate_product(self, property: str) -> object:
        if property is not None and not isinstance(property, str):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR, f"property 只支持str类型参数, 传入类型为{type(property)}"
            )

        invoke_args = {
            "collection": self,
            "property": property,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        if "property" not in invoke_args:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "参数property不能为空")

        return FunctionHelper.apply(
            "ImageCollection.aggregate_product", "object", invoke_args
        )

    def aggregate_sample_sd(self, property: str) -> object:
        if property is not None and not isinstance(property, str):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR, f"property 只支持str类型参数, 传入类型为{type(property)}"
            )

        invoke_args = {
            "collection": self,
            "property": property,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        if "property" not in invoke_args:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "参数property不能为空")

        return FunctionHelper.apply(
            "ImageCollection.aggregate_sample_sd", "object", invoke_args
        )

    def aggregate_sample_var(self, property: str) -> object:
        if property is not None and not isinstance(property, str):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR, f"property 只支持str类型参数, 传入类型为{type(property)}"
            )

        invoke_args = {
            "collection": self,
            "property": property,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        if "property" not in invoke_args:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "参数property不能为空")

        return FunctionHelper.apply(
            "ImageCollection.aggregate_sample_var", "object", invoke_args
        )

    def aggregate_total_sd(self, property: str) -> object:
        if property is not None and not isinstance(property, str):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR, f"property 只支持str类型参数, 传入类型为{type(property)}"
            )

        invoke_args = {
            "collection": self,
            "property": property,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        if "property" not in invoke_args:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "参数property不能为空")

        return FunctionHelper.apply(
            "ImageCollection.aggregate_total_sd", "object", invoke_args
        )

    def aggregate_total_var(self, property: str) -> object:
        if property is not None and not isinstance(property, str):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR, f"property 只支持str类型参数, 传入类型为{type(property)}"
            )

        invoke_args = {
            "collection": self,
            "property": property,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        if "property" not in invoke_args:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "参数property不能为空")

        return FunctionHelper.apply(
            "ImageCollection.aggregate_total_var", "object", invoke_args
        )

    def aggregate_histogram(self, property: str) -> object:
        if property is not None and not isinstance(property, str):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR, f"property 只支持str类型参数, 传入类型为{type(property)}"
            )

        invoke_args = {
            "collection": self,
            "property": property,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        if "property" not in invoke_args:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "参数property不能为空")

        return FunctionHelper.apply(
            "ImageCollection.aggregate_histogram", "object", invoke_args
        )

    def aggregate_count_distinct(self, property: str) -> object:
        if property is not None and not isinstance(property, str):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR, f"property 只支持str类型参数, 传入类型为{type(property)}"
            )

        invoke_args = {
            "collection": self,
            "property": property,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        if "property" not in invoke_args:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "参数property不能为空")

        return FunctionHelper.apply(
            "ImageCollection.aggregate_count_distinct", "object", invoke_args
        )

    def aggregate_first(self, property: str) -> object:
        if property is not None and not isinstance(property, str):
            raise AIEError(
                AIEErrorCode.ARGS_ERROR, f"property 只支持str类型参数, 传入类型为{type(property)}"
            )

        invoke_args = {
            "collection": self,
            "property": property,
        }

        invoke_args = {k: v for k, v in invoke_args.items() if v is not None}

        if "property" not in invoke_args:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "参数property不能为空")

        return FunctionHelper.apply(
            "ImageCollection.aggregate_first", "object", invoke_args
        )
