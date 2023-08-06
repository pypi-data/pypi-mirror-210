#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import annotations

import os
import time
import aie
from .client.task import Task
from .error.aie_error import AIEError, AIEErrorCode
from .client.dataset import Dataset
from .g_var import GVarKey, has_var, get_var
from .auth import Authenticate


class Export(object):
    class image(object):
        @staticmethod
        def toAsset(image: aie.Image, assetId: str, scale: int = 1000, config: dict = None):
            if not isinstance(image, aie.Image):
                raise AIEError(AIEErrorCode.ARGS_ERROR,
                               f"image 只支持 aie.Image 类型参数, 传入类型为{type(image)}")
            if not isinstance(assetId, str):
                raise AIEError(AIEErrorCode.ARGS_ERROR,
                               f"assetId 只支持 str 类型参数, 传入类型为{type(image)}")

            options = {
                "taskType": "ExportImage",
                "assetId": assetId,
                "scale": scale,
                "function": "image.toAsset"
            }

            if config is not None:
                options["config"] = config
            return Task(image, options)

    class feature(object):
        @staticmethod
        def toAsset(featureCollection: aie.FeatureCollection, assetId: str, config: dict = None):
            if not isinstance(featureCollection, aie.FeatureCollection):
                raise AIEError(AIEErrorCode.ARGS_ERROR,
                               f"featureCollection 只支持 aie.FeatureCollection 类型参数, 传入类型为{type(featureCollection)}")
            if not isinstance(assetId, str):
                raise AIEError(AIEErrorCode.ARGS_ERROR,
                               f"assetId 只支持 str 类型参数, 传入类型为{type(featureCollection)}")

            options = {
                "taskType": "ExportFeature",
                "assetId": assetId,
                "function": "feature.toAsset"
            }

            if config is not None:
                options["config"] = config
            return Task(featureCollection, options)

    class dataset(object):
        SUPPORT_SUFFIX = ["csv", "xls", "xlsx", "txt", "md", "jar", "png", "jpg", "jpeg",
                          "mp4", "avi", "acc", "mp3", "wmv", "h5", "bin", "pdf", "html", "json", "zip"]

        @staticmethod
        def toAsset(name: str, args: Union[str, list]):
            if not (has_var(GVarKey.Authenticate.CLIENT_ID) and get_var(GVarKey.Authenticate.CLIENT_ID) == Authenticate.ClientId.ALIYUN_JUPYTER):
                raise AIEError(AIEErrorCode.ARGS_ERROR,
                               f"aie.Export.feature.toAsset 只支持在AIE云平台jupyter环境里面调用")

            if not isinstance(name, str):
                raise AIEError(AIEErrorCode.ARGS_ERROR,
                               f"name 只支持 str 类型参数, 传入类型为{type(name)}")

            files = args
            if isinstance(args, str):
                files = [args]

            if not all(isinstance(file, str) for file in files):
                raise AIEError(AIEErrorCode.ARGS_ERROR,
                               f"args 只支持 str|list[str] 类型参数, 传入类型为{type(args)}")

            files_with_suffix = []
            for file in files:
                if not os.path.exists(file):
                    raise AIEError(AIEErrorCode.ARGS_ERROR,
                                   f"文件{file}路径不存在")

                _, suffix = os.path.splitext(file)
                suffix = suffix[1:]
                if suffix not in Export.dataset.SUPPORT_SUFFIX:
                    raise AIEError(AIEErrorCode.ARGS_ERROR,
                                   f"文件类型{suffix}不支持，支持的文件后缀类型为:{Export.dataset.SUPPORT_SUFFIX}")

                files_with_suffix.append((file, suffix))

            dataset = Dataset(name)
            for file, suffix in files_with_suffix:
                print(f"上传文件中: {file}")
                dataset.upload(file, suffix)

            dataset.publish()
            print("正在导出数据集...")
            while(dataset.active()):
                time.sleep(5)

            print(dataset.status())
