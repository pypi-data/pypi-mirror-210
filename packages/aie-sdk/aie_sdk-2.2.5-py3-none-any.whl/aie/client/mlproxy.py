#!/usr/bin/env python
# -*- coding: utf-8 -*-

import oss2
from typing import Optional
from .endpoints import *
from .client import *
from pystac_client import Client
from .constants import *
from aie.error import AIEError, AIEErrorCode
from multiprocessing.dummy import Pool as ThreadPool


class MachineLearningProxyClient(BaseClient):

    class ResponseCode(object):
        RESP_STATUS_CODE_OK = 0
        RESP_STATUS_CODE_ERR = -1

        KEY_HTTP_RESP_CODE = "code"
        KEY_HTTP_RESP_PAYLOAD = "payload"
        KEY_HTTP_RESP_HEADERS = "headers"
        KEY_HTTP_RESP_MSG = "msg"
        KEY_HTTP_RESP_PAYLOAD_JOB_LOGVIEW = "jobLogview"
        # KEY_HTTP_RESP_UID = "x-aie-uid"

    @staticmethod
    def post(url, data, append_extra_hdrs=True) -> dict:
        headers = {"Content-Type": "application/json"}
        resp = super(MachineLearningProxyClient, MachineLearningProxyClient).post(
            url, headers, data, append_extra_hdrs)
        resp_dict = resp.json()
        MachineLearningProxyClient.__check_response_status(resp_dict)
        return resp_dict

    @staticmethod
    def get(url, append_extra_hdrs=True) -> dict:
        headers = {"Content-Type": "application/json"}
        resp = super(MachineLearningProxyClient, MachineLearningProxyClient).get(
            url, headers, append_extra_hdrs)
        resp_dict = resp.json()

        MachineLearningProxyClient.__check_response_status(resp_dict)
        return resp_dict

    @classmethod
    def get_oss_object(cls, object_name: str, file_path: str, access_key_id: str,
                       access_key_secret: str, security_token: str, oss_host: str, oss_bucket_name: str) -> str:
        res = "Failed !"
        auth = oss2.StsAuth(access_key_id, access_key_secret, security_token)
        bucket = oss2.Bucket(auth, oss_host, oss_bucket_name)
        resp = bucket.get_object_to_file(object_name, file_path)
        if resp.resp.status == 200:
            res = "Success !"
        return res

    @classmethod
    def put_oss_object(cls, object_name: str, file_path: str, access_key_id: str,
                       access_key_secret: str, security_token: str, oss_host: str, oss_bucket_name: str) -> str:
        res = "Failed !"
        auth = oss2.StsAuth(access_key_id, access_key_secret, security_token)
        bucket = oss2.Bucket(auth, oss_host, oss_bucket_name)
        resp = bucket.put_object_from_file(object_name, file_path)
        if resp.resp.status == 200:
            res = "Success !"
        return res

    @classmethod
    def __check_response_status(cls, resp_dict):
        if resp_dict.get(MachineLearningProxyClient.ResponseCode.KEY_HTTP_RESP_CODE) != \
                MachineLearningProxyClient.ResponseCode.RESP_STATUS_CODE_OK:
            err_msg = resp_dict.get(
                MachineLearningProxyClient.ResponseCode.KEY_HTTP_RESP_MSG)
            raise AIEError(AIEErrorCode.DEFAULT_INTERNAL_ERROR,
                           "", f"请求错误：{err_msg}")

    @classmethod
    def __get_headers(cls, resp_dict) -> dict:
        return resp_dict.get(MachineLearningProxyClient.ResponseCode.KEY_HTTP_RESP_HEADERS, {})

    @classmethod
    def __get_payload(cls, resp_dict) -> dict:
        return resp_dict.get(MachineLearningProxyClient.ResponseCode.KEY_HTTP_RESP_PAYLOAD, {})


class MlProxy(object):

    class OssStsInfo(object):
        KEY_OSS_BUCKET_NAME = "ossBucketName"
        KEY_OSS_ENDPOINT = "ossEndpoint"
        KEY_ACCESS_KEY_ID = "ossStsAccessKeyId"
        KEY_ACCESS_KEY_SECRET = "ossStsAccessKeySecret"
        KEY_SECURITY_TOKEN = "ossStsAccessSecurityToken"
        KEY_USER_WORK_DIR = "userWorkDir"

    @staticmethod
    def __get_oss_info(oss_root_dir='', oss_bucket_name='', oss_endpoint=''):
        method_name = "getOssInfo?ossRootDir={}&ossBucketName={}&ossEndpoint={}"
        url = Endpoints.ML_PROXY_HOST + method_name.format(oss_root_dir, oss_bucket_name, oss_endpoint)
        resp_dict = MachineLearningProxyClient.get(url, append_extra_hdrs=True)
        payload = {}
        if resp_dict[MachineLearningProxyClient.ResponseCode.KEY_HTTP_RESP_CODE] == \
                MachineLearningProxyClient.ResponseCode.RESP_STATUS_CODE_OK:
            payload = resp_dict[MachineLearningProxyClient.ResponseCode.KEY_HTTP_RESP_PAYLOAD]

        return payload

    @staticmethod
    def __get_pai_job_base_param() -> dict:
        oss_info_dict = MlProxy.__get_oss_info()
        bucket_name = oss_info_dict.get(MlProxy.OssStsInfo.KEY_OSS_BUCKET_NAME)
        user_work_dir = oss_info_dict.get(MlProxy.OssStsInfo.KEY_USER_WORK_DIR)
        pai_oss_endpoint = "oss-cn-hangzhou-internal.aliyuncs.com"
        default_cluster_dict = {'worker': {'gpu': 100}}

        data = {PAI_JOB_PARAM_NAME: 'pytorch_ext',
                PAI_JOB_PARAM_PROJECT: 'algo_public',
                PAI_JOB_PARAM_SCRIPT: 'oss://' + bucket_name + '.' + pai_oss_endpoint + '/' + user_work_dir,
                PAI_JOB_PARAM_PYTHON: '3.6',
                PAI_JOB_PARAM_OSS_HOST: pai_oss_endpoint,
                PAI_JOB_PARAM_INPUTS: 'oss://' + bucket_name + '.' + pai_oss_endpoint + '/' + user_work_dir,
                PAI_JOB_PARAM_CHECKPOINT_DIR: 'oss://' + bucket_name + '.' + pai_oss_endpoint + '/' + user_work_dir,
                PAI_JOB_PARAM_CLUSTER: json.dumps(default_cluster_dict, ensure_ascii=False)}

        return data

    @staticmethod
    def __save_credentials(cred_dict):
        cred_dict_json = json.dumps(cred_dict, ensure_ascii=False)
        os.makedirs(DEFAULT_CREDENTIALS_DIR, exist_ok=True)
        cred_file_path = os.path.join(
            DEFAULT_CREDENTIALS_DIR, CREDENTIALS_FILE_NAME)
        with open(cred_file_path, 'w') as f:
            f.write(cred_dict_json)

    @staticmethod
    def __save_pai_tmp_credentials(cred_dict, target_dir):
        cred_dict_json = json.dumps(cred_dict, ensure_ascii=False)
        os.makedirs(target_dir, exist_ok=True)
        cred_file_path = os.path.join(target_dir, PAI_TMP_CREDENTIALS_FILE_NAME)
        with open(cred_file_path, 'w') as f:
            f.write(cred_dict_json)

    @staticmethod
    def __load_credentials():
        error_msg = "--MlProxy认证信息不存在或已过期，请先执行MlProxy.run_init()初始化MlProxy模块!"
        cred_file_path = os.path.join(
            DEFAULT_CREDENTIALS_DIR, CREDENTIALS_FILE_NAME)
        if not os.path.exists(cred_file_path):
            raise AIEError(AIEErrorCode.DEFAULT_INTERNAL_ERROR,
                           "", error_msg)
        with open(cred_file_path, "r") as f:
            res = json.loads(f.readlines()[0])
        return res

    @staticmethod
    def __gen_frontend_logview_url(token, instanceId):
        if not token or not instanceId:
            err_msg = "token and instanceId cant be empty."
            raise AIEError(message=err_msg)
        url = Endpoints.HOST + "/#/misc/logview?" + "token=" + token + "&" + "instanceId=" + instanceId
        return url

    @staticmethod
    def save_tmp_cred(target_dir):
        oss_info_dict = MlProxy.__get_oss_info()
        MlProxy.__save_pai_tmp_credentials(oss_info_dict, target_dir)

    @staticmethod
    def get_oss_object(object_name, file_path, oss_root_dir='', oss_bucket_name='', oss_endpoint=''):
        # Get oss info
        # oss_info_dict = MlProxy.__load_credentials()
        oss_info_dict = MlProxy.__get_oss_info(oss_root_dir, oss_bucket_name, oss_endpoint)

        if not oss_root_dir or not oss_bucket_name or not oss_endpoint:
            object_name = os.path.join(oss_info_dict.get(MlProxy.OssStsInfo.KEY_USER_WORK_DIR), object_name)

        resp = MachineLearningProxyClient.get_oss_object(object_name,
                                                         file_path,
                                                         oss_info_dict.get(
                                                             MlProxy.OssStsInfo.KEY_ACCESS_KEY_ID, ""),
                                                         oss_info_dict.get(
                                                             MlProxy.OssStsInfo.KEY_ACCESS_KEY_SECRET, ""),
                                                         oss_info_dict.get(
                                                             MlProxy.OssStsInfo.KEY_SECURITY_TOKEN, ""),
                                                         oss_info_dict.get(
                                                             MlProxy.OssStsInfo.KEY_OSS_ENDPOINT, ""),
                                                         oss_info_dict.get(MlProxy.OssStsInfo.KEY_OSS_BUCKET_NAME, ""))
        return resp

    @staticmethod
    def put_oss_object(object_name, file_path, oss_root_dir='', oss_bucket_name='', oss_endpoint=''):
        # Get oss info
        # oss_info_dict = MlProxy.__load_credentials()
        oss_info_dict = MlProxy.__get_oss_info(oss_root_dir, oss_bucket_name, oss_endpoint)
        if not oss_root_dir or not oss_bucket_name or not oss_endpoint:
            object_name = os.path.join(oss_info_dict.get(MlProxy.OssStsInfo.KEY_USER_WORK_DIR), object_name)

        resp = MachineLearningProxyClient.put_oss_object(object_name,
                                                         file_path,
                                                         oss_info_dict.get(
                                                             MlProxy.OssStsInfo.KEY_ACCESS_KEY_ID, ""),
                                                         oss_info_dict.get(
                                                             MlProxy.OssStsInfo.KEY_ACCESS_KEY_SECRET, ""),
                                                         oss_info_dict.get(
                                                             MlProxy.OssStsInfo.KEY_SECURITY_TOKEN, ""),
                                                         oss_info_dict.get(
                                                             MlProxy.OssStsInfo.KEY_OSS_ENDPOINT, ""),
                                                         oss_info_dict.get(MlProxy.OssStsInfo.KEY_OSS_BUCKET_NAME, ""))

        return resp


    @staticmethod
    def __print_info():
        import time
        for i in range(5):
            print("任务提交中 ...")
            time.sleep(2)
        print("任务提交成功!")

    @staticmethod
    def __run_post(args):
        return MachineLearningProxyClient.post(url=args[0], data=args[1], append_extra_hdrs=True)

    @staticmethod
    def commit_model_job(data: dict) -> dict:
        """
        Commit model training job to cluster.
        :param data:
        :return:
        """
        method_name = "commitJob"
        url = Endpoints.ML_PROXY_HOST + method_name

        base_params_dict = MlProxy.__get_pai_job_base_param()
        if PAI_JOB_PARAM_SCRIPT in data:
            base_params_dict[PAI_JOB_PARAM_SCRIPT] = os.path.join(base_params_dict[PAI_JOB_PARAM_SCRIPT],
                                                                  data[PAI_JOB_PARAM_SCRIPT])
            data.pop(PAI_JOB_PARAM_SCRIPT)

        if PAI_JOB_PARAM_INPUTS in data:
            base_params_dict[PAI_JOB_PARAM_INPUTS] = os.path.join(base_params_dict[PAI_JOB_PARAM_INPUTS],
                                                                  data[PAI_JOB_PARAM_INPUTS])
            data.pop(PAI_JOB_PARAM_INPUTS)

        if PAI_JOB_PARAM_CHECKPOINT_DIR in data:
            base_params_dict[PAI_JOB_PARAM_CHECKPOINT_DIR] = os.path.join(base_params_dict[PAI_JOB_PARAM_CHECKPOINT_DIR],
                                                                          data[PAI_JOB_PARAM_CHECKPOINT_DIR])
            data.pop(PAI_JOB_PARAM_CHECKPOINT_DIR)

        base_params_dict.update(data)

        # print info during connecting
        pool = ThreadPool(2)

        resp = pool.apply_async(MlProxy.__run_post, ((url, base_params_dict),))
        pool.apply_async(MlProxy.__print_info)

        pool.close()
        pool.join()
        resp = resp.get()

        payload = {}
        if resp[MachineLearningProxyClient.ResponseCode.KEY_HTTP_RESP_CODE] == \
                MachineLearningProxyClient.ResponseCode.RESP_STATUS_CODE_OK:
            payload = resp[MachineLearningProxyClient.ResponseCode.KEY_HTTP_RESP_PAYLOAD]

        token = resp['headers']['x-aie-auth-token']
        sub_instance_id = payload['subInstanceId']
        ret_msg = resp[MachineLearningProxyClient.ResponseCode.KEY_HTTP_RESP_MSG]

        front_url = MlProxy.__gen_frontend_logview_url(token=token, instanceId=sub_instance_id)
        payload[MachineLearningProxyClient.ResponseCode.KEY_HTTP_RESP_PAYLOAD_JOB_LOGVIEW] = front_url

        return payload

    @staticmethod
    def get_job_logview(sub_instance_id: str) -> str:
        method_name = "getJobLogview?subInstanceId={}"
        url = Endpoints.ML_PROXY_HOST + method_name.format(sub_instance_id)
        resp = MachineLearningProxyClient.get(url=url, append_extra_hdrs=True)
        payload = ""
        if resp[MachineLearningProxyClient.ResponseCode.KEY_HTTP_RESP_CODE] == \
                MachineLearningProxyClient.ResponseCode.RESP_STATUS_CODE_OK:
            payload = resp[MachineLearningProxyClient.ResponseCode.KEY_HTTP_RESP_PAYLOAD]

        token = resp['headers']['x-aie-auth-token']
        front_url = MlProxy.__gen_frontend_logview_url(token=token, instanceId=sub_instance_id)

        return front_url

    @staticmethod
    def get_job_status(job_id: str) -> str:
        method_name = "getJobStatus?subInstanceId={}"
        url = Endpoints.ML_PROXY_HOST + method_name.format(job_id)
        resp = MachineLearningProxyClient.get(url=url, append_extra_hdrs=True)
        payload = ""
        if resp[MachineLearningProxyClient.ResponseCode.KEY_HTTP_RESP_CODE] == \
                MachineLearningProxyClient.ResponseCode.RESP_STATUS_CODE_OK:
            payload = resp[MachineLearningProxyClient.ResponseCode.KEY_HTTP_RESP_PAYLOAD]
        return payload

    @staticmethod
    def stop_job(job_id: str) -> str:
        method_name = "stopJob?jobId={}"
        url = Endpoints.ML_PROXY_HOST + method_name.format(job_id)
        resp = MachineLearningProxyClient.get(url=url, append_extra_hdrs=True)
        payload = ""
        if resp[MachineLearningProxyClient.ResponseCode.KEY_HTTP_RESP_CODE] == \
                MachineLearningProxyClient.ResponseCode.RESP_STATUS_CODE_OK:
            payload = resp[MachineLearningProxyClient.ResponseCode.KEY_HTTP_RESP_PAYLOAD]
        return payload

    @staticmethod
    def get_stac_dataset(dataset_id: str,
                         collection: Optional[str] = DEFAULT_STAC_AIE_ML_COLLECTION) -> dict:
        res = {}
        stac_client = Client.open(Endpoints.STAC_ENDPOINT)

        search_result = stac_client.search(collections=collection)
        for item in search_result.items():
            if not item.id == dataset_id:
                continue
            item = item.to_dict()
            res = {
                'train_path': item.get('assets').get('train').get('href'),
                'valid_path': item.get('assets').get('valid').get('href'),
                'test_path': item.get('assets').get('test').get('href'),
                'train_mapping_path': item.get('assets').get('train_mapping').get('href'),
                'class_dict_path': item.get('assets').get('class_dict').get('href')
            }
        return res

    @staticmethod
    def list_stac_datasets(collection: Optional[str] = DEFAULT_STAC_AIE_ML_COLLECTION) -> None:
        stac_client = Client.open(Endpoints.STAC_ENDPOINT)
        search_result = stac_client.search(collections=collection)
        for idx, item in enumerate(search_result.items()):
            print(">Dataset-" + str(idx + 1) + ":")
            print("    id:", json.dumps(item.id, indent=4))
            print("    properties:", json.dumps(item.properties))
            print("\n")
