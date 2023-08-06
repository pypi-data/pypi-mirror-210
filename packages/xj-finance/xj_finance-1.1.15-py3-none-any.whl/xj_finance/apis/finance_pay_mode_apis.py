# _*_coding:utf-8_*_

import os, logging, time, json, copy

from django.views.decorators.http import require_http_methods
from rest_framework.views import APIView

from utils.custom_tool import request_params_wrapper
from xj_finance.services.finance_pay_mode_service import FinancePayModeService
from xj_finance.services.finance_transact_service import FinanceTransactService
from xj_finance.services.finance_transacts_service import FinanceTransactsService
from xj_finance.utils.user_wrapper import user_authentication_wrapper
from ..utils.model_handle import util_response
from ..services.finance_service import FinanceService

logger = logging.getLogger(__name__)


class FinancePayModeApi(APIView):  # 或继承(APIView)

    # 支付方式添加
    @require_http_methods(['POST'])
    @user_authentication_wrapper
    @request_params_wrapper
    def add(self, *args, user_info, request_params, **kwargs, ):
        params = request_params
        pay_mode_set, err = FinancePayModeService.add(params)
        if err is None:
            return util_response(data=pay_mode_set)
        return util_response(err=47767, msg=err)

    # 支付方式修改
    @require_http_methods(['PUT'])
    @user_authentication_wrapper
    @request_params_wrapper
    def edit(self, *args, user_info, request_params, **kwargs, ):
        params = request_params
        pay_mode_set, err = FinancePayModeService.edit(params)
        if err is None:
            return util_response(data=pay_mode_set)
        return util_response(err=47767, msg=err)

    # 支付方式列表
    @require_http_methods(['GET'])
    @user_authentication_wrapper
    @request_params_wrapper
    def list(self, *args, user_info, request_params, **kwargs, ):
        pay_mode_set, err = FinancePayModeService.list()
        if err is None:
            return util_response(data=pay_mode_set)
        return util_response(err=47767, msg=err)
