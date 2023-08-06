# _*_coding:utf-8_*_

import os, logging, time, json, copy

from django.views.decorators.http import require_http_methods
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.views import APIView

from utils.custom_tool import request_params_wrapper
from xj_finance.services.finance_transact_service import FinanceTransactService
from xj_finance.utils.custom_tool import flow_service_wrapper
from xj_finance.utils.user_wrapper import user_authentication_force_wrapper, user_authentication_wrapper
from xj_user.services.user_service import UserService
from ..services.finance_transacts_service import FinanceTransactsService
from ..utils.model_handle import parse_data, util_response
from ..services.finance_service import FinanceService

logger = logging.getLogger(__name__)


# 获取余额
class FinanceBalance(APIView):  # 或继承(APIView)

    @require_http_methods(['GET'])
    @user_authentication_wrapper
    @request_params_wrapper
    def get(self, *args, user_info, request_params, **kwargs, ):
        params = request_params
        # ============   字段验证处理 start ============
        user_id = user_info.get("user_id")
        platform_id = user_info.get("platform_id")
        params.setdefault("user_id", user_id)  # 用户ID

        data = FinanceService.check_balance(account_id=user_id, platform=None,
                                            platform_id=platform_id, currency='CNY',
                                            sand_box=None)

        return util_response(data=data)

    @require_http_methods(['POST'])
    @user_authentication_wrapper
    @request_params_wrapper
    def cash_withdrawal(self, *args, user_info, request_params, **kwargs,):
        params = request_params
        user_id = user_info.get("user_id")
        platform_id = user_info.get("platform_id")
        params.setdefault("account_id", user_id)  # 用户ID
        cash_withdrawal_set, err = FinanceTransactService.finance_flow_writing(params=params, finance_type='WITHDRAW')
        if err is None:
            return util_response(data=cash_withdrawal_set)

        return util_response(err=47767, msg=err)
