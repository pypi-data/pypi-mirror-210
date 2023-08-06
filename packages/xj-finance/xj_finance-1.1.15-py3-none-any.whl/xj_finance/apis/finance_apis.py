# _*_coding:utf-8_*_

import os, logging, time, json, copy

from django.views.decorators.http import require_http_methods
from rest_framework.views import APIView

from ..utils.custom_tool import request_params_wrapper, flow_service_wrapper
from xj_finance.services.finance_transact_service import FinanceTransactService
from xj_finance.services.finance_transacts_service import FinanceTransactsService
from xj_finance.utils.user_wrapper import user_authentication_wrapper
from ..utils.model_handle import util_response
from ..services.finance_service import FinanceService

logger = logging.getLogger(__name__)


class FinanceApi(APIView):  # 或继承(APIView)

    # 财务添加
    @require_http_methods(['POST'])
    @user_authentication_wrapper
    @request_params_wrapper
    def add(self, *args, user_info, request_params, **kwargs, ):
        params = request_params
        user_id = user_info.get("user_id")
        platform_id = user_info.get("platform_id")
        params.setdefault("account_id", user_id)  # 用户ID
        transact_set, err = FinanceTransactService.add(params)
        if err is None:
            return util_response(data=transact_set)
        return util_response(err=47767, msg=err)

    # 财务修改
    @require_http_methods(['PUT'])
    @user_authentication_wrapper
    @request_params_wrapper
    def edit(self, *args, user_info, request_params, **kwargs, ):
        params = request_params
        user_id = user_info.get("user_id")
        platform_id = user_info.get("platform_id")
        params.setdefault("account_id", user_id)  # 用户ID
        transact_set, err = FinanceTransactService.add(params)
        if err is None:
            return util_response(data=transact_set)
        return util_response(err=47767, msg=err)

    # 财务列表
    @require_http_methods(['GET'])
    @user_authentication_wrapper
    @request_params_wrapper
    def list(self, *args, user_info, request_params, **kwargs, ):
        params = request_params
        # ============   字段验证处理 start ============
        user_id = user_info.get("user_id")
        params.setdefault("user_id", user_id)  # 用户ID

        transact_set, err = FinanceTransactsService.list(params, user_id)

        if err is None:
            return util_response(data=transact_set)

        return util_response(err=47767, msg=err)

    # 财务详细
    @require_http_methods(['GET'])
    @user_authentication_wrapper
    @request_params_wrapper
    def detail(self, *args, user_info, request_params, **kwargs, ):
        params = request_params
        # ============   字段验证处理 start ============
        user_id = user_info.get("user_id")
        params.setdefault("user_id", user_id)  # 用户ID
        transact_set, err = FinanceTransactsService.detail(params.get("finance_id", 0))
        # transact_set, err = FinanceTransactsService.detail(params.get("finance_id", 0))
        if err is None:
            return util_response(data=transact_set)
        return util_response(err=47767, msg=err)

    # 查询余额
    @require_http_methods(['GET'])
    @user_authentication_wrapper
    @request_params_wrapper
    def balance(self, *args, user_info, request_params, **kwargs, ):
        params = request_params
        # ============   字段验证处理 start ============
        user_id = user_info.get("user_id")
        platform_id = user_info.get("platform_id")
        data = FinanceService.check_balance(account_id=user_id, platform=None,
                                            platform_id=platform_id, currency='CNY',
                                            sand_box=None)
        return util_response(data=data)

    # 财务提现
    @require_http_methods(['POST'])
    @user_authentication_wrapper
    @request_params_wrapper
    def cash_withdrawal(self, *args, user_info, request_params, **kwargs, ):
        params = request_params
        user_id = user_info.get("user_id")
        platform_id = user_info.get("platform_id")
        params.setdefault("account_id", user_id)  # 用户ID
        cash_withdrawal_set, err = FinanceTransactService.finance_flow_writing(params=params, finance_type='WITHDRAW')
        if err is None:
            return util_response(data=cash_withdrawal_set)
        return util_response(err=47767, msg=err)

    # 大额转账
    @require_http_methods(['POST'])
    @user_authentication_wrapper
    @request_params_wrapper
    @flow_service_wrapper
    def large_transfer(self, *args, user_info, request_params, **kwargs, ):
        params = request_params
        user_id = user_info.get("user_id")
        platform_id = user_info.get("platform_id")
        params.setdefault("account_id", user_id)  # 用户ID
        data, err_txt = FinanceTransactService.finance_flow_writing(params=params, finance_type='OFFLINE')
        if err_txt is None:
            return util_response(data=data)
        return util_response(err=47767, msg=err_txt)

    # 财务审批（核销、红冲、提现状态、转账）
    @require_http_methods(['POST'])
    @user_authentication_wrapper
    @request_params_wrapper
    @flow_service_wrapper
    def examine_approve(self, *args, user_info, request_params, **kwargs, ):
        params = request_params
        user_id = user_info.get("user_id")
        platform_id = user_info.get("platform_id")
        params.setdefault("account_id", user_id)  # 用户ID
        data, err_txt = FinanceTransactsService.examine_approve(params)
        if err_txt is None:
            return util_response(data=data)
        return util_response(err=47767, msg=err_txt)
