# _*_coding:utf-8_*_

import os, logging, time, json, copy

from django.views.decorators.http import require_http_methods
from rest_framework.views import APIView

from utils.custom_tool import request_params_wrapper
from xj_finance.services.finance_currency_service import FinanceCurrencyService
from xj_finance.services.finance_transact_service import FinanceTransactService
from xj_finance.services.finance_transacts_service import FinanceTransactsService
from xj_finance.utils.user_wrapper import user_authentication_wrapper
from ..utils.model_handle import util_response
from ..services.finance_service import FinanceService

logger = logging.getLogger(__name__)


class FinanceCurrencyApi(APIView):  # 或继承(APIView)

    # 币种添加
    @require_http_methods(['POST'])
    @user_authentication_wrapper
    @request_params_wrapper
    def add(self, *args, user_info, request_params, **kwargs, ):
        params = request_params
        currency_set, err = FinanceCurrencyService.add(params)
        if err is None:
            return util_response(data=currency_set)
        return util_response(err=47767, msg=err)

    @require_http_methods(['PUT'])
    @user_authentication_wrapper
    @request_params_wrapper
    def edit(self, *args, user_info, request_params, **kwargs, ):
        params = request_params
        currency_set, err = FinanceCurrencyService.edit(params)
        if err is None:
            return util_response(data=currency_set)
        return util_response(err=47767, msg=err)

    # 财务币种列表
    @require_http_methods(['GET'])
    @user_authentication_wrapper
    @request_params_wrapper
    def list(self, *args, user_info, request_params, **kwargs, ):
        params = request_params
        user_id = user_info.get("user_id")
        params.setdefault("user_id", user_id)  # 用户ID
        currency_set, err = FinanceCurrencyService.list()
        if err is None:
            return util_response(data=currency_set)
        return util_response(err=47767, msg=err)
