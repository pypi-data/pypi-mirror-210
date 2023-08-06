#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import base64

from traitlets import HasTraits, Union, List, Unicode, Float, validate, Integer

import json
import aie
from ipyleaflet import projections, WMSPostLayer, WMSLayer
from aie.client import Endpoints
from aie.auth import Authenticate
from aie.error import AIEError, AIEErrorCode
from collections.abc import Iterable

from aie.map import aie_color


class ImageVisParams(HasTraits):
    bands = Union(
        [List(Integer()), Integer(), Unicode(), List(Unicode())], default_value=None, allow_none=True
    ).tag(desc="list of band names (or single band) to be mapped to RGB")
    min = Union([List(Float()), Float()], default_value=None, allow_none=True).tag(
        desc="min values (or one per band) to map onto 00."
    )
    max = Union([List(Float()), Float()], default_value=None, allow_none=True).tag(
        desc="max values (or one per band) to map onto FF."
    )
    gain = Union([List(Float()), Float()], default_value=None, allow_none=True).tag(
        desc="gain values (or one per band) to map onto 00-FF."
    )
    bias = Union([List(Float()), Float()], default_value=None, allow_none=True).tag(
        desc="bias values (or one per band) to map onto FF."
    )
    gamma = Union([List(Float()), Float()], default_value=None, allow_none=True).tag(
        desc="gamma correction factors (or one per band)."
    )
    palette = List(Unicode(), minlen=2, default_value=None, allow_none=True).tag(
        desc="color palette for single band render"
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def symbolize_params(self):
        to_8bit_method = "ColorRamp" if self.palette is not None else "MinMaxStretch"
        to_8bit_params = (
            self.color_map_params()
            if self.palette is not None
            else self.stretch_params()
        )
        return {
            "symbolizeMethodNames": [to_8bit_method],
            "symbolizeMethodParams": {to_8bit_method: to_8bit_params},
        }

    def color_map_params(self):
        min_value = (
            (0 - self.bias[0] / self.gain[0]) if self.min is None else self.min[0]
        )
        max_value = (
            (255 - self.bias[0] / self.gain[0]) if self.max is None else self.max[0]
        )
        color_value = min_value
        color_value_step = (max_value - min_value) / (len(self.palette) - 1)
        color_map = []
        for color in self.palette:
            color_map.append({"value": color_value, "color": color})
            color_value += color_value_step
        return {"renderMode": 1, "colorMap": color_map}

    def stretch_params(self):
        bands = len(self.gain) if self.min is None else len(self.min)
        min_values = (
            [0 - self.bias[i] / self.gain[i] for i in range(bands)]
            if self.min is None
            else self.min
        )
        max_values = (
            [255 - self.bias[i] / self.gain[i] for i in range(bands)]
            if self.max is None
            else self.max
        )
        return {
            "fromMinMaxPerBand": [[min_values[i], max_values[i]] for i in range(bands)]
        }

    @validate("bands")
    def _validate_bands(self, proposal):
        bands = proposal["value"]
        if bands is None:
            return bands
        elif not isinstance(bands, list):
            return [bands]
        elif len(bands) != 1 and len(bands) != 3:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "选择的波段数必须为 1 或 3")
        else:
            return bands

    @validate("min", "max", "gain", "bias", "gamma")
    def _validate_stretch_params(self, proposal):
        name = proposal["trait"].name
        if name in ["min", "max"] and (self.min is None or self.max is None):
            raise AIEError(AIEErrorCode.ARGS_ERROR, "必须同时设置 min 和 max！")
        elif name in ["gain", "bias"]:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "暂时不支持 gain 和 bias！")
        elif self.min is not None and self.gain is not None:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "不能同时设置 min/max 和 gain/bias！")
        values = proposal["value"]
        if not isinstance(values, list):
            return [values] * 1 if self.bands is None else len(self.bands)
        elif len(values) == 1:
            return values * 1 if self.bands is None else len(self.bands)
        else:
            return values

    @validate("palette")
    def _validate_palette(self, proposal):
        palette_colors = proposal["value"]
        if self.min is None and self.gain is None:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "palette 使用需要设置 min/max 或 gain/bias")
        for color in palette_colors:
            if len(color) != 7:
                raise AIEError(AIEErrorCode.ARGS_ERROR, "颜色 '%s' 格式不满足要求, 例子: '#FFFFFF'" % color)
            try:
                int(color[1:], 16)
            except ValueError:
                raise AIEError(AIEErrorCode.ARGS_ERROR, "颜色 '%s' 格式不满足要求, 例子: '#FFFFFF'" % color)
        return palette_colors


class AIEImageLayer(WMSLayer):
    token = Unicode().tag(sync=True, o=True)
    aie_map_id = Unicode().tag(sync=True, o=True)

    def __init__(self, name: str, aie_object: aie.Image, vis_params: dict, **kwargs):
        if "bounds" not in kwargs:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "当前需要显式指定 aie_object 的 bounds")
        if "crs" in kwargs.keys():
            kwargs.pop("crs")
            print("warning. 暂不支持坐标系设置，默认为EPSG4326")

        bounds = kwargs["bounds"]
        bounds = [[bounds[1], bounds[0]], [bounds[3], bounds[2]]]
        kwargs.pop("bounds")

        if 'palette' in vis_params.keys() \
                and isinstance(vis_params['palette'], Iterable):
            # valid only one band provided if palette exsits
            if 'bands' in vis_params \
                    and not isinstance(vis_params['bands'], str) \
                    and isinstance(vis_params['bands'], Iterable) \
                    and len(vis_params['bands']) > 1:
                raise ValueError('调色盘模式(Palette)仅支持一个波段的渲染')
            vis_params['palette'] = [aie_color.translate_color(color) for color in vis_params['palette']]
        image_vis_params = ImageVisParams(**vis_params)
        if image_vis_params.bands is not None:
            aie_object = aie_object.select(image_vis_params.bands)
        map_id = aie_object.getMapId(vis_params)
        new_kwargs = {
            "name": name,
            "url": Endpoints.MAP,
            "bounds": bounds,
            "layers": "async_aie_map_raster",
            "crs": projections.EPSG4326,
            "aie_map_id": 'Maps_mapId_' + map_id["mapId"],
            "camel_case": False,
            "attribution": "AIE Engine",
            "token": Authenticate.getCurrentUserToken(),
        }
        new_kwargs.update(kwargs)
        super().__init__(**new_kwargs)


class AIEGeometryLayer(WMSLayer):
    token = Unicode().tag(sync=True, o=True)
    aie_map_id = Unicode().tag(sync=True, o=True)

    def __init__(self, name: str, aie_object: aie.Geometry, vis_params: dict, **kwargs):
        if "bounds" not in kwargs:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "当前需要显式指定 aie_object 的 bounds")
        bounds = kwargs["bounds"]
        bounds = [[bounds[1], bounds[0]], [bounds[3], bounds[2]]]
        kwargs.pop("bounds")
        if 'color' in vis_params and isinstance(vis_params['color'], str):
            vis_params['color'] = aie_color.translate_color(vis_params['color'])
        if 'styles' in vis_params and isinstance(vis_params['styles'], Iterable):
            for style in vis_params['styles']:
                if isinstance(style, dict):
                    style['color'] = aie_color.translate_color(style['color'])
        if "color" not in vis_params:
            vis_params["color"] = "#000000"
        map_id = aie_object.getMapId(vis_params)
        new_kwargs = {
            "name": name,
            "url": Endpoints.MAP_VECTOR,
            "bounds": bounds,
            "layers": "mpg",
            "crs": projections.EPSG4326,
            "token": Authenticate.getCurrentUserToken(),
            "aie_map_id": 'Maps_mapId_' + map_id["mapId"],
            "attribution": "AIE Engine",
            "camel_case": False
        }
        new_kwargs.update(kwargs)
        super().__init__(**new_kwargs)
