import sys
import time
import os
import datetime

from django.db.models import Q
from django.db.models import F
from django.forms import model_to_dict

from xj_user.services.user_detail_info_service import DetailInfoService
from xj_user.services.user_platform_service import UserPlatformService
from ..models import *
from ..models import StatusCode
from decimal import Decimal
from ..utils.custom_tool import format_params_handle


class FinanceService:

    def __init__(self):
        pass

    # crc16
    @staticmethod
    def crc16(x):
        a = 0xFFFF
        b = 0xA001
        for byte in x:
            a ^= ord(byte)
            for i in range(8):
                last = a % 2
                a >>= 1
                if last == 1:
                    a ^= b
        s = hex(a).upper()

        return s[2:6]

    # 保留两位小数
    @staticmethod
    def keep_two_decimal_places(str_num):
        result_num = format(float(str_num), "")

        if len(result_num.split(".")[-1]) < 2:
            result_num = result_num + "0"
        return result_num

    # 检查账号余额是否正确
    @staticmethod
    def check_balance(account_id='', platform='', platform_id=None, currency='', sand_box=''):

        # ========== 一、内容的类型准确性检查 ==========
        account, account_err = DetailInfoService.get_detail(account_id)
        if account_err:
            return {'err': 7001, 'msg': 'check_balance: account_id不存在:' + str(account_id)}
        if platform:
            platform_info, error = UserPlatformService.get_platform_info(platform_name=platform)
            if error:
                return {'err': 7002, 'msg': 'check_balance: platform不存在' + str(platform)}
            platform_id = platform_info.get('platform_id', 0)
        elif platform_id:
            platform_id = platform_id
        else:
            platform_id = 0
        currency_set = Currency.objects.filter(currency=currency).first()
        if not currency_set:
            return {'err': 7003, 'msg': 'check_balance: currency不存在' + str(currency)}

        sand_box = sand_box if sand_box else None
        sand_box_set = None
        if sand_box:
            sand_box_set = SandBox.objects.filter(sand_box_name=sand_box).first()
        if sand_box and not sand_box_set:
            return {'err': 7004, 'msg': 'check_balance: sand_box不存在' + str(sand_box)}

        # ========== 二、相关前置业务逻辑处理 ==========
        transact_set = Transact.objects.filter(
            Q(account_id=account_id) &
            Q(platform_id=platform_id) &
            Q(currency__currency=currency)
        )

        if sand_box is None:
            transact_set = transact_set.filter(Q(sand_box__sand_box_name__isnull=True))
        else:
            transact_set = transact_set.filter(Q(sand_box__sand_box_name=sand_box))

        transact_set = transact_set.order_by('transact_time')

        for i, it in enumerate(transact_set):
            is_inside_pay = True if str(it.pay_mode).upper() == 'BALANCE' else False
            income = it.income if it.income else Decimal(0.0)
            outgo = it.outgo if it.outgo else Decimal(0.0)
            if is_inside_pay:
                if i == 0:
                    balance = income - outgo
                    if balance != it.balance:
                        it.balance = balance
                        it.save()
                    continue

                last = transact_set[i - 1]
                balance = last.balance + income - outgo
                if balance != it.balance:
                    it.balance = balance
                    it.save()
        transact_set_new = Transact.objects.filter(
            Q(account_id=account_id) &
            Q(platform_id=platform_id) &
            Q(currency__currency=currency)
        )
        if sand_box is None:
            transact_set_new = transact_set_new.filter(Q(sand_box__sand_box_name__isnull=True))
        else:
            transact_set_new = transact_set_new.filter(Q(sand_box__sand_box_name=sand_box))
        transact_set_new = transact_set_new.order_by('-transact_time').first()
        if transact_set_new:
            transact_set_new = model_to_dict(transact_set_new)
            if not sys.modules.get("xj_finance.service.finance_transact_service.FinanceTransactService"):
                from xj_finance.services.finance_transact_service import FinanceTransactService
                balance = FinanceTransactService.keep_two_decimal_places(transact_set_new['balance'])
            return {"balance": balance}

        return {"balance": 0}

        # return True

    # 生成交易号：2位数（当前年份后2位数字）+8位数（当前时间戳去头2位）+6位数（用户名 经过hash crc16生成的 4位十六进制 转成5位数 然后头为补0）
    @staticmethod
    def make_unicode(salt=''):
        # 当前时间戳
        date_time = time.localtime(time.time())
        # 截取第3位到第4位
        year_code = str(date_time.tm_year)[2:4]

        # 当前时间戳
        timestamp = str(int(time.time()))
        # 截取第3位到第10位
        timestamp_code = timestamp[2:10]

        # 十六进制校验码
        crc_hex = FinanceService.crc16(salt) if salt else '0'
        # 十六进制转十进制
        crc_int = int(crc_hex, 16)
        # 头位补0
        crc_code = str('000000' + str(crc_int))[-6:]
        unicode = year_code + timestamp_code + crc_code

        return unicode

    # 检查过滤筛选的有效性函数
    @staticmethod
    def check_filter_validity(params={}):
        """
        检查过滤筛选的有效性函数
        :param params: 要检查的参数列表
        :return: 可用于查询的查询集
        """

        query_dict = {}

        # 搜索平台
        platform_name = params.get('platform', '')
        if platform_name:
            platform_set, err = UserPlatformService.get_platform_info(platform_name=platform_name)
            if err:
                return {'err': 3001, 'msg': 'platform不存在', }
            query_dict['platform_id'] = platform_set['platform_id']

        finance_status_code = params.get('finance_status_code', '')
        if finance_status_code:
            sand_box_set = StatusCode.objects.filter(finance_status_code=finance_status_code).first().id
            # print("1",sand_box_set)
            if not sand_box_set:
                return {'err': 3001, 'msg': 'finance_status_code不存在', }
            query_dict['finance_status_code'] = sand_box_set

        # 搜索币种
        currency = params.get('currency', '')
        if currency:
            currency_set = Currency.objects.filter(Q(currency=currency)).first()
            if not currency_set:
                return {'err': 3002, 'msg': 'currency不存在', }
            query_dict['currency__currency'] = currency

        # 搜索支付方式
        pay_mode = params.get('pay_mode', '')
        if pay_mode:
            pay_mode_set = PayMode.objects.filter(Q(pay_mode=pay_mode)).first()
            if not pay_mode_set:
                return {'err': 3003, 'msg': 'pay_mode不存在', }
            query_dict['pay_mode__pay_mode'] = pay_mode

        sand_box_list = params.get('sand_box_list', '')
        if sand_box_list:
            sand_box_list = sand_box_list.split(',')
            sand_box_set = SandBox.objects.filter(Q(sand_box_name__in=sand_box_list)).first()
            if not sand_box_set:
                return {'err': 3004, 'msg': 'sand_box不存在', }
            query_dict['sand_box__sand_box_name__in'] = sand_box_list
        # 搜索沙盒
        sand_box = params.get('sand_box', '')
        if sand_box:
            sand_box_set = SandBox.objects.filter(Q(sand_box_name=sand_box)).first()
            if sand_box and not sand_box_set:
                return {'err': 3004, 'msg': 'sand_box不存在', }
            query_dict['sand_box__sand_box_name'] = sand_box
        elif not sand_box and not sand_box_list:
            # 显示非沙盒（即真实交易）
            # if sand_box is False:
            query_dict['sand_box__sand_box_name__isnull'] = True

        # 模糊搜索对方账号
        their_account_name = params.get('their_account_name', '')
        if their_account_name:
            query_dict['their_account__full_name__icontains'] = their_account_name

        # 模糊搜索摘要search_word
        search_word = params.get('search_word', '')
        if search_word:
            query_dict['summary__icontains'] = search_word

        # 精确匹配沙盒状态
        sand_box_status_code = params.get('sand_box_status_code', '')
        if sand_box_status_code:
            query_dict['sand_box_status_code'] = sand_box_status_code

        return {'err': 0, 'msg': 'OK', 'query_dict': query_dict, }

    # 财务余额校对
    @staticmethod
    def balance_validation(request_params):
        # transact_set = Transact.objects.filter()
        account_id = request_params.get("account_id")
        platform_id = request_params.get("platform_id")

        transact_set = Transact.objects.filter(
            Q(account_id=account_id) &
            Q(platform_id=platform_id) &
            Q(sand_box_id__isnull=True)
        ).order_by('id')

        transact_set.filter(Q(pay_mode__pay_mode__in=['TRANSFER', 'WECHAT'])).update(balance=0)
        first_record = transact_set.exclude(pay_mode__pay_mode__in=['TRANSFER', 'WECHAT']).first()
        first_record = model_to_dict(first_record)
        if first_record['income'] > first_record['outgo']:
            balance = first_record['income']
        else:
            balance = first_record['outgo']
        Transact.objects.filter(id=first_record['id']).update(balance=balance)
        record = transact_set.exclude(pay_mode__pay_mode__in=['TRANSFER', 'WECHAT']).values("id", "income", "outgo")
        for i in list(record):
            if i['income'] > i['outgo']:
                balance += i['income']
            else:
                balance -= i['outgo']
            Transact.objects.filter(id=i['id']).update(balance=balance)
            # print(balance)
        return None, None
        # transact_set.values("income","outgo")
