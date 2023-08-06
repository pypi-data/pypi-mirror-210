# _*_coding:utf-8_*_

import os, logging, time, json, copy
import re
from datetime import datetime, timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import response
from rest_framework import serializers
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django.db.models import Q
from django.db.models import F
from django.db.models import Sum, Count
from decimal import Decimal
import pytz
from django.http import HttpResponse, JsonResponse
from django.utils.translation import gettext as _

from ..models import *
from xj_user.services.user_service import UserService
from ..utils.model_handle import parse_data, util_response
from ..services.finance_transacts_service import FinanceTransactsService

logger = logging.getLogger(__name__)


class FinanceTransacts(generics.UpdateAPIView):  # 或继承(APIView)
    """ REST framework的APIView实现获取card列表 """

    # authentication_classes = (TokenAuthentication,)  # token认证
    # permission_classes = (IsAuthenticated,)   # IsAuthenticated 仅通过认证的用户
    # permission_classes = (AllowAny,)  # 允许所有用户 (IsAuthenticated,IsStaffOrBureau)
    # serializer_class = FinanceTransactsSerializer
    # params = None  # 请求体的原始参数
    #
    # print("-" * 30, os.path.basename(__file__), "-" * 30)

    def get(self, request, *args, **kwargs):

        # ========== 一、验证权限 ==========

        token = self.request.META.get('HTTP_AUTHORIZATION', '')
        if not token:
            return util_response(err=4001, msg='缺少Token')

        # print("get token:", token)
        data, err_txt = UserService.check_token(token)
        # print("get data, err_txt:", data, err_txt)
        if not data:
            return util_response(err=4002, msg=err_txt)

        # ========== 二、必填性检查 ==========

        params = parse_data(request)
        data, err_txt = FinanceTransactsService.get(params, data['user_id'])
        if not data:
            return util_response(err=4002, msg=err_txt)

        return Response({
            'err': 0,
            'msg': 'OK',
            'data': data
        })

    # 核销
    def write_off(self):
        params = parse_data(self)
        print(params)
        data, err_txt = FinanceTransactsService.examine_approve(params)
        if err_txt is None:
            return util_response(data=data)
        return util_response(err=47767, msg=err_txt)

    # 开票时间
    def invoicing_approval(self):
        params = parse_data(self)
        data, err_txt = FinanceTransactsService.invoicing_approval(params)
        if err_txt is None:
            return util_response(data=data)
        return util_response(err=47767, msg=err_txt)


    # 大额转账
    def large_transfer(self):
        token = self.META.get('HTTP_AUTHORIZATION', '')
        if not token:
            return util_response(err=4001, msg='缺少Token')

        # print("get token:", token)
        data, err_txt = UserService.check_token(token)
        # print("get data, err_txt:", data, err_txt)
        if not data:
            return util_response(err=4002, msg=err_txt)
        params = parse_data(self)
        params['account_id'] = data['user_id']
        data, err_txt = FinanceTransactsService.large_transfer(params)
        if err_txt is None:
            return util_response(data=data)
        return util_response(err=47767, msg=err_txt)

    # 大额转账审核结果查询
    def large_amount_audit(self):
        token = self.META.get('HTTP_AUTHORIZATION', '')
        if not token:
            return util_response(err=4001, msg='缺少Token')

        # print("get token:", token)
        data, err_txt = UserService.check_token(token)
        # print("get data, err_txt:", data, err_txt)
        if not data:
            return util_response(err=4002, msg=err_txt)
        params = parse_data(self)
        params['account_id'] = data['user_id']
        data, err_txt = FinanceTransactsService.large_amount_audit(params)
        if err_txt is None:
            return util_response(data=data)
        return util_response(err=47767, msg=err_txt)

    # 应收应付生成
    def create_or_write_off(self):
        params = parse_data(self)
        data, err = FinanceTransactsService.finance_create_or_write_off(params)
        if err is None:
            return util_response(data=data)
        return util_response(err=47767, msg=err)


