#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import requests
from .endpoints import *
from .client import Client
from aie.serialize import serializer
import aie


class Maps(object):
    class AddLayerType:
        Image = "Image"
        Feature = "Feature"

    @staticmethod
    def getMapId(obj, vis_params=None):
        request_id = newUUID()

        add_layer_type = None
        if isinstance(obj, aie.Image):
            add_layer_type = Maps.AddLayerType.Image
        elif isinstance(obj, aie.ImageCollection):
            obj = obj.mosaic()
            add_layer_type = Maps.AddLayerType.Image
        elif isinstance(obj, aie.Geometry):
            add_layer_type = Maps.AddLayerType.Feature
        elif isinstance(obj, aie.Feature):
            add_layer_type = Maps.AddLayerType.Feature
        elif isinstance(obj, aie.FeatureCollection):
            add_layer_type = Maps.AddLayerType.Feature

        expr = serializer.encode(obj)

        options = {
            "mapId": newUUID(),
            "taskType": "addLayer",
            "addLayerType": add_layer_type,
            "visParams": vis_params
        }

        options_serialize = ""
        try: 
            options_serialize = json.dumps(options, ensure_ascii=False, allow_nan=False)
        except Exception as e:
            raise aie.error.AIEError(aie.error.AIEErrorCode.ARGS_ERROR, "请检查visParams参数", str(e))
        data = {"requestId": request_id,
                "expr": expr,
                "options": options_serialize}

        url = Endpoints.SDK_GATEWAY + SdkGatewayResource.Maps.GET_MAP_ID
        return Client.post(url, data)
