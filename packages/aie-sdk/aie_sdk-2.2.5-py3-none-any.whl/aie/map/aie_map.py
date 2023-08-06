#!/usr/bin/env python
# -*- coding: utf-8 -*-
import collections.abc
from typing import Iterator

import aie
import ipyleaflet
from ipyleaflet import projections, basemaps
from .aie_layer import AIEImageLayer, AIEGeometryLayer
from aie.error import AIEError, AIEErrorCode

# init the aie_color module when aie_map module is initialized
from aie.map import aie_color
aie_color.init()


def _layer_name_generator(i: int = 1) -> Iterator:
    while True:
        yield "Layer %d" % i
        i += 1


class Map(ipyleaflet.Map):
    def __init__(self, **kwargs):
        self._layer_name_iterator = _layer_name_generator()
        # crs
        if "crs" in kwargs.keys():
            kwargs.pop("crs")
            print("warning. 暂不支持坐标系设置，默认为EPSG4326")
        # center
        if "location" in kwargs.keys():
            kwargs["center"] = kwargs["location"]
            kwargs.pop("location")
        if "center" not in kwargs.keys():
            # Beijing
            kwargs["center"] = (116.383331, 39.916668)
        else: 
            center = kwargs["center"]
            kwargs["center"] = (center[1], center[0])
        # zoom
        if "zoom_start" in kwargs.keys():
            kwargs["zoom"] = kwargs["zoom_start"]
            kwargs.pop("zoom_start")
        if "zoom" not in kwargs.keys():
            kwargs["zoom"] = 2
        if "max_zoom" not in kwargs.keys():
            kwargs["max_zoom"] = 18
        # attribution_control
        if "attribution_control" not in kwargs.keys():
            kwargs["attribution_control"] = False
        # style
        if "height" not in kwargs.keys():
            self._height = "600px"
        else:
            if isinstance(kwargs["height"], int):
                self._height = str(kwargs["height"]) + "px"
            else:
                self._height = kwargs["height"]
            kwargs.pop("height")
        if "width" not in kwargs.keys():
            self._width = "100%"
        else:
            if isinstance(kwargs["width"], int):
                self._width = str(kwargs["width"]) + "px"
            else:
                self._width = kwargs["width"]
            kwargs.pop("width")
        # controls
        lite_mode = False
        if "lite_mode" in kwargs.keys():
            lite_mode = kwargs["lite_mode"]
            kwargs.pop("lite_mode")
        self._has_layers_control = (
            kwargs["layers_control"]
            if "layers_control" in kwargs.keys()
            else not lite_mode
        )
        self._has_scale_ctrl = (
            kwargs["scale_ctrl"] if "scale_ctrl" in kwargs.keys() else not lite_mode
        )
        self._has_fullscreen_ctrl = (
            kwargs["fullscreen_ctrl"]
            if "fullscreen_ctrl" in kwargs.keys()
            else not lite_mode
        )
        self._has_measure_ctrl = (
            kwargs["measure_ctrl"] if "measure_ctrl" in kwargs.keys(
            ) else not lite_mode
        )

        super().__init__(**kwargs)

        self.layout.height = self._height
        self.layout.width = self._width
        if self._has_layers_control:
            self.add_control(ipyleaflet.LayersControl(position="topright"))
        if self._has_scale_ctrl:
            self.add_control(ipyleaflet.ScaleControl(position="bottomleft"))
        if self._has_fullscreen_ctrl:
            self.add_control(ipyleaflet.FullScreenControl())
        if self._has_measure_ctrl:
            self.add_control(
                ipyleaflet.MeasureControl(
                    position="bottomleft",
                    active_color="orange",
                    primary_length_unit="kilometers",
                )
            )

    def add_aie_layer(
        self, aie_object, vis_params, name=None, show=True, opacity=1.0, **kwargs
    ):
        # # try to translate color palette
        # if isinstance(vis_params, dict) \
        #     and 'palette' in vis_params.keys() \
        #         and isinstance(vis_params['palette'], collections.abc.Iterable):
        #     vis_params['palette'] = [aie_color.translate_color(color) for color in vis_params['palette']]

        if name is None:
            name = self._layer_name_iterator.__next__()
        kwargs.update(
            {
                "visible": show,
                "opacity": opacity,
                "format": "image/png",
                "transparent": True,
            }
        )
        if isinstance(aie_object, (aie.Image, aie.ImageCollection)):
            self.add_layer(AIEImageLayer(
                name, aie_object, vis_params, **kwargs))
        elif isinstance(aie_object, (aie.Geometry, aie.Feature, aie.FeatureCollection)):
            self.add_layer(AIEGeometryLayer(
                name, aie_object, vis_params, **kwargs))
        else:
            raise AIEError(AIEErrorCode.ARGS_ERROR, "对于类型 %s 的 layer 未实现" % type(aie_object))

    projections = projections
    addLayer = add_aie_layer
