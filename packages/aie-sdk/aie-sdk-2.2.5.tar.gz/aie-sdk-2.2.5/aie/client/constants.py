#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path
from os.path import expanduser

DEFAULT_STAC_AIE_ML_COLLECTION = "AIE_PUBLIC_DATA_ML"

# keys of PAI Job params
PAI_JOB_PARAM_NAME = "name"
PAI_JOB_PARAM_PROJECT = "project"
PAI_JOB_PARAM_SCRIPT = "script"
PAI_JOB_PARAM_ENTRYFILE = "entryFile"
PAI_JOB_PARAM_INPUTS = "inputs"
PAI_JOB_PARAM_CHECKPOINT_DIR = "checkpointDir"
PAI_JOB_PARAM_WORKER_COUNT = "workerCount"
PAI_JOB_PARAM_OSS_HOST = "ossHost"
PAI_JOB_PARAM_PYTHON = "python"
PAI_JOB_PARAM_CLUSTER = "cluster"
PAI_JOB_PARAM_HYPER_PARAMETERS = "hyperParameters"

# local credentials
DEFAULT_CREDENTIALS_DIR = expanduser(Path.home().joinpath('.mlproxy', 'credentials'))
CREDENTIALS_FILE_NAME = "sts_info"
PAI_TMP_CREDENTIALS_FILE_NAME = ".tmp_info"