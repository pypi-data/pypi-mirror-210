# _*_coding:utf-8_*_

import os, logging, time, json, copy

from django.views.decorators.http import require_http_methods
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.views import APIView

from utils.custom_tool import request_params_wrapper
from xj_finance.utils.user_wrapper import user_authentication_wrapper
from ..utils.model_handle import parse_data, util_response
from ..services.finance_status_code_service import FinanceStatusCodeService

logger = logging.getLogger(__name__)


# 获取付款类型
class FinanceStatusCodeApis(APIView):  # 或继承(APIView)

    # 付款类型添加
    @require_http_methods(['POST'])
    @user_authentication_wrapper
    @request_params_wrapper
    def add(self, *args, user_info, request_params, **kwargs, ):
        params = request_params
        pay_mode_set, err = FinanceStatusCodeService.add(params)
        if err is None:
            return util_response(data=pay_mode_set)
        return util_response(err=47767, msg=err)

    # 付款类型修改
    @require_http_methods(['PUT'])
    @user_authentication_wrapper
    @request_params_wrapper
    def edit(self, *args, user_info, request_params, **kwargs, ):
        params = request_params
        pay_mode_set, err = FinanceStatusCodeService.edit(params)
        if err is None:
            return util_response(data=pay_mode_set)
        return util_response(err=47767, msg=err)

    # 付款类型列表
    @require_http_methods(['GET'])
    @user_authentication_wrapper
    @request_params_wrapper
    def list(self, *args, user_info, request_params, **kwargs, ):
        pay_mode_set, err = FinanceStatusCodeService.list()
        if err is None:
            return util_response(data=pay_mode_set)
        return util_response(err=47767, msg=err)

