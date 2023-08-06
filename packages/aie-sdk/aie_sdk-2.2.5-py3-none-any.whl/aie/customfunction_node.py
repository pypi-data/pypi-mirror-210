#!/usr/bin/env python
# -*- coding: utf-8 -*-

import aie
from aie.serialize import serializer


class CustomFunctionNode(object):
    def __init__(self, arg_names, body):
        self.arg_names = arg_names
        self.body = body
