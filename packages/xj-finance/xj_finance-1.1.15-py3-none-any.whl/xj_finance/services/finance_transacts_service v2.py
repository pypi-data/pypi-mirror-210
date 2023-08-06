from decimal import Decimal
import json
from logging import getLogger
from pathlib import Path
import sys

from django.db.models import Sum, F
from django.forms import model_to_dict
import pytz
from rest_framework import serializers

from main.settings import BASE_DIR
from xj_enroll.utils.custom_tool import format_params_handle
from xj_finance.services.finance_transact_service import FinanceTransactService
from xj_finance.utils.custom_tool import filter_result_field
from xj_thread.services.thread_list_service import ThreadListService
from xj_thread.utils.join_list import JoinList
from xj_user.models import BaseInfo, Platform
from xj_user.services.user_platform_service import UserPlatformService
from .finance_service import FinanceService
from ..models import Transact, PayMode
from ..utils.j_config import JConfig
from ..utils.j_dict import JDict

logger = getLogger('log')

module_root = str(Path(__file__).resolve().parent)
# 配置之对象
main_config_dict = JDict(JConfig.get_section(path=str(BASE_DIR) + "/config.ini", section="xj_finance"))
module_config_dict = JDict(JConfig.get_section(path=str(BASE_DIR) + "/config.ini", section="xj_finance"))

sand_box_meet = main_config_dict.sand_box_meet or module_config_dict.sand_box_meet or ""
sand_box_receivable = main_config_dict.sand_box_receivable or module_config_dict.sand_box_receivable or ""
sand_box_cash_withdrawal = main_config_dict.sand_box_cash_withdrawal or module_config_dict.sand_box_cash_withdrawal or ""


# 声明用户序列化
class UserSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        return BaseInfo.objects.create(**validated_data)

    class Meta:
        model = BaseInfo
        # 序列化验证检查，是否要必填的字典
        fields = ['id', 'platform_uid', 'full_name', 'platform_id']


class FinanceTransactsSerializer(serializers.ModelSerializer):
    # 方法一：使用SerializerMethodField，并写出get_platform, 让其返回你要显示的对象就行了
    # p.s.SerializerMethodField在model字段显示中很有用。
    # order = serializers.SerializerMethodField()
    lend = serializers.SerializerMethodField()
    amount = serializers.SerializerMethodField()
    balance = serializers.SerializerMethodField()
    transact_time = serializers.SerializerMethodField()
    # transact_timestamp = serializers.SerializerMethodField()
    sand_box = serializers.SerializerMethodField()
    # finance_status_code = serializers.SerializerMethodField()

    # # 方法二：增加一个序列化的字段platform_name用来专门显示品牌的name。当前前端的表格columns里对应的’platform’列要改成’platform_name’
    # account_id = serializers.ReadOnlyField(source='account.id')
    account_name = serializers.ReadOnlyField(source='account.full_name')
    # their_account_id = serializers.ReadOnlyField(source='their_account.id')
    their_account_name = serializers.ReadOnlyField(source='their_account.full_name')
    # platform_id = serializers.ReadOnlyField(source='platform.platform_id')
    # platform_name = serializers.ReadOnlyField(source='platform.platform_name')
    # platform = serializers.ReadOnlyField(source='platform.platform_name')
    pay_mode = serializers.ReadOnlyField(source='pay_mode.pay_mode')
    currency = serializers.ReadOnlyField(source='currency.currency')

    # income = serializers.ReadOnlyField(source='income')
    # outgo = serializers.ReadOnlyField(source='outgo')

    class Meta:
        model = Transact
        fields = [
            # 'order',
            'id',
            # 'transact_no',
            'transact_no',
            "thread_id",
            "enroll_id",
            'transact_time',
            # 'transact_timestamp',
            'platform_id',
            # 'platform_name',
            # 'platform',
            # 'account_id',
            'account_name',
            # 'their_account_id',
            'their_account_name',
            'order_no',
            'opposite_account',
            'summary',
            'currency',
            'income',
            'outgo',
            'lend',
            'amount',
            'balance',
            'pay_mode',
            'goods_info',
            # 'pay_info',
            'sand_box',
            'remark',
            'images',
            'is_reverse',
            'is_delete',
            'is_write_off',
            'finance_status_code',
            "sand_box_status_code",
            # "snapshot"
        ]

    # def get_order(self, obj):
    #     print("get_order:", obj.id, obj, self)
    #     return 1

    def get_lend(self, obj):
        income = obj.income if obj.income is not None else Decimal(0)
        outgo = obj.outgo if obj.outgo is not None else Decimal(0)
        amount = income - outgo
        return '借' if amount < 0 else '贷' if amount > 0 else '平'

    def get_amount(self, obj):
        income = obj.income if obj.income is not None else Decimal(0)
        outgo = obj.outgo if obj.outgo is not None else Decimal(0)
        return income - outgo

    def get_balance(self, obj):
        balance = obj.balance
        return balance

    def get_sand_box(self, obj):
        return obj.sand_box.sand_box_name if obj.sand_box else None

    def get_transact_time(self, obj):
        return obj.transact_time.astimezone(tz=pytz.timezone('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S')

    # def get_transact_timestamp(self, obj):
    #     return int(obj.transact_time.timestamp())


class FinanceTransactsService:
    @staticmethod
    def get(params, user_id):
        # ========== 三、内容的类型准确性检查 ==========
        valid = FinanceService.check_filter_validity(params=params)
        # print(">>> check_filter_validity", valid)
        if valid['err'] > 0:
            # return Response({'err': valid['err'], 'msg': valid['msg'], })
            return None, valid['msg']
        if params.get("is_all", None):
            transacts = Transact.objects.filter(**valid['query_dict'])
        else:
            transacts = Transact.objects.filter(account_id=user_id).filter(**valid['query_dict'])

        if params.get("is_enroll", None):
            transacts = Transact.objects.filter(enroll_id__isnull=False).filter(**valid['query_dict'])
        if params.get("is_thread", None):
            transacts = Transact.objects.filter(thread_id__isnull=False).filter(**valid['query_dict'])

        transacts = transacts.order_by('-transact_time')
        # print(params['transact_time_start'])
        if params.get("transact_time_start", None) and params.get("transact_time_end", None):
            transacts = transacts.filter(
                transact_time__range=(params['transact_time_start'], params['transact_time_end']))

        # transacts = transacts.extra(select={'platform_name':'SELECT platform_name FROM user_platform WHERE user_platform.platform_id = finance_transact.platform_id'})

        # print(">>> transacts: ", transacts)

        # statistic_list = []
        # aggr = transacts.aggregate(
        #     outgo=Sum('outgo', filter=Q(currency__currency='CNY')),
        #     income=Sum('income', filter=Q(currency__currency='CNY')),
        # )
        # aggr['income'] = aggr['income'] or Decimal(0.0)
        # aggr['outgo'] = aggr['outgo'] or Decimal(0.0)
        # aggr['balance'] = aggr['income'] - aggr['outgo']
        # statistic_list.append(aggr)

        # images = 'http://' + request.headers['Host'] + ''

        # ========== 四、相关前置业务逻辑处理 ==========

        # ========== 五、翻页 ==========

        page = int(params['page']) - 1 if 'page' in params else 0
        size = int(params['size']) if 'size' in params else 10

        total = transacts.count()
        income = transacts.aggregate(income=Sum("income"))
        outgo = transacts.aggregate(outgo=Sum("outgo"))

        current_page_set = transacts[page * size: page * size + size] if page >= 0 and size > 0 else transacts

        serializer = FinanceTransactsSerializer(current_page_set, many=True)

        res_list = []
        for i, it in enumerate(serializer.data):
            # print("current_page_set:", i, it)
            it['order'] = page * size + i + 1
            # it['platform_name'] = params.get('platform', '')
            res_list.append(it)
        # return {'total': total, 'list': res_list, 'statistics': statistic_list}, None
        data = res_list
        thread_id_list = [item.get("thread_id", None) for item in res_list]
        thread_list, err = ThreadListService.search(thread_id_list)
        if thread_list:
            data = JoinList(res_list, thread_list, "thread_id", "id").join()

        statistics = {
            "income": income.get("income", 0.0) if income.get("income", 0.0) else 0.0,
            "outgo": outgo.get("outgo", 0.0) if outgo.get("outgo", 0.0) else 0.0,
        }
        # enroll_id_list = [item.get("enroll_id", None) for item in res_list]
        # thread_list, err = ThreadListService.search(thread_id_list)
        # if thread_list:
        #     data = JoinList(res_list, thread_list, "thread_id", "id").join()
        # print(enroll_id_list)

        return {'size': int(size), 'page': int(page + 1), 'total': total, 'list': data, "statistics": statistics}, None

        # return {'total': total, 'list': res_list}, None
        # 翻译
        # output = _("Welcome to my site.")

        # return Response({
        #     'err': 0,
        #     'msg': 'OK',
        #     'data': {'total': total, 'list': res_list, 'statistics': statistic_list},
        #     # 'data': output,
        # })

    @staticmethod
    def detail(pk=None, order_no=None, transact_no=None, field_list=None):
        """
        查询订单性情
        """
        if not pk and not order_no and not transact_no:
            return None, None

        transact_obj = Transact.objects

        if pk:
            transact_filter_obj = transact_obj.filter(id=pk).first()
        elif order_no:
            transact_filter_obj = transact_obj.filter(order_no=order_no).first()
        elif transact_no:
            transact_filter_obj = transact_obj.filter(transact_no=transact_no).first()
        else:
            return None, "没有找到对应的数据"

        if not transact_filter_obj:
            return None, "没有找到对应的数据"

        transact_dict = transact_filter_obj.to_json()

        transact_filter_dict = format_params_handle(
            param_dict=transact_dict,
            filter_filed_list=field_list
        )
        return transact_filter_dict, None

    @staticmethod
    def detail_all(order_no=None):
        """
        查询订单详情
        """
        if not order_no:
            return None, None

        transact_obj = Transact.objects

        if order_no:
            transact_filter_obj = transact_obj.filter(
                order_no=order_no, sand_box__isnull=False).values("order_no", "transact_no", "goods_info",
                                                                  "account_id",
                                                                  "enroll_id",
                                                                  "their_account_id",
                                                                  "platform_id",
                                                                  "income", "outgo", "balance",
                                                                  "currency_id", "pay_mode_id",
                                                                  "summary", "finance_status_code")
        else:
            return None, "没有找到对应的数据"

        if not transact_filter_obj:
            return None, "没有找到对应的数据"

        # print(model_to_list(transact_filter_obj))
        return transact_filter_obj, None

    @staticmethod
    def distribution(params):
        order_no = params.get("order_no", "")
        applicant_person_id = params.get("applicant_person_id", "")
        payment_category = params.get("payment_category  ", "meet")  # 款项类目 receivable 应收 meet 应付
        amount = params.get('amount', 0.0)  # 如果是负数是应付反之是应收
        two_level = params.get('two_level', "")  # 是否为二级分销
        receivable_data = {}  # 应收数据
        meet_data = {}  # 应付数据
        # 查询交易信息
        finance_transact_data, err = FinanceTransactsService.detail(order_no=order_no)
        if err:
            return None, err
        else:
            # if two_level == 'True':
            #     two_level = True
            # elif two_level == 'False':
            #     two_level = False
            # 获取交易流水号
            # transact_no = finance_transact_data['transact_no'].rstrip(finance_transact_data['transact_no'][-1])
            # 获取报名id
            enroll_id = finance_transact_data['enroll_id']
            # 应收数据
            meet_data['sand_box'] = sand_box_receivable  # 沙盒应收
            meet_data['transact_no'] = FinanceService.make_unicode(str(applicant_person_id))  # 流水号
            meet_data['amount'] = amount
            meet_data['account_id'] = applicant_person_id  # 报名人id
            meet_data['their_account_id'] = finance_transact_data['their_account_id']
            meet_data['order_no'] = order_no  # 订单号
            meet_data['currency_id'] = finance_transact_data['currency_id']  # 币种
            meet_data['pay_mode_id'] = finance_transact_data['pay_mode_id']  # 支付方式
            meet_data['platform_id'] = finance_transact_data['platform_id']  # 所属平台
            meet_data['summary'] = finance_transact_data['summary']  # 摘要说明
            meet_data['finance_status_code'] = 2  # 资金状态码 finance_status_code 242 报名成功 待付款

            # 应付数据
            receivable_data['sand_box'] = sand_box_meet  # 沙盒应付
            receivable_data['transact_no'] = FinanceService.make_unicode(
                str(finance_transact_data['their_account_id']))  # 流水号
            receivable_data['amount'] = -abs(float(amount))
            receivable_data['account_id'] = finance_transact_data['their_account_id']
            receivable_data['their_account_id'] = applicant_person_id
            receivable_data['order_no'] = order_no  # 订单号
            receivable_data['currency_id'] = finance_transact_data['currency_id']  # 币种
            receivable_data['pay_mode_id'] = finance_transact_data['pay_mode_id']  # 支付方式
            receivable_data['platform_id'] = finance_transact_data['platform_id']  # 所属平台
            receivable_data['summary'] = finance_transact_data['summary']  # 摘要说明
            receivable_data['finance_status_code'] = 2  # 资金状态码  finance_status_code 242 报名成功 待付款

            # while True:
            #     number = ''.join(str(x) for x in random.sample(range(10), 3))
            #     number1 = ''.join(str(x) for x in random.sample(range(10), 3))
            #     if not number.startswith('0') and not number1.startswith('0'):
            #         break
            # if enroll_id:
            #     meet_data['enroll_id'] = enroll_id
            #     receivable_data['enroll_id'] = enroll_id
            # if two_level:
            #     # 生成不重复的 订单流水号
            #     while True:
            #         receivable_data['transact_no'] = transact_no.rstrip(receivable_data['transact_no'][-1]) + str(
            #             int(receivable_data['transact_no'][-1]) + int(number))
            #         meet_data['transact_no'] = transact_no.rstrip(meet_data['transact_no'][-1]) + str(
            #             int(meet_data['transact_no'][-1]) + int(number1))
            #
            #         receivable = Transact.objects.filter(transact_no=receivable_data['transact_no']).exists()
            #         meet = Transact.objects.filter(transact_no=meet_data['transact_no']).exists()
            #         if not receivable and not meet:
            #             break

            print("应付", receivable_data)
            receivable_finance_transact, receivable_err = FinanceTransactService.post(receivable_data)
            if receivable_err:
                return None, receivable_err
            print("应收", meet_data)
            meet_finance_transact, meet_err = FinanceTransactService.post(meet_data)
            if meet_err:
                return None, meet_err
            return None, None

    @staticmethod
    def write_off(params):
        order_no = params.get("order_no", "")
        type = params.get("type", "")
        images = params.get("images", "")
        finance_transact_data, err = FinanceTransactsService.detail_all(order_no=order_no)
        if err:
            return None, err
        for v in finance_transact_data:
            transact_no = v['transact_no']
            if type == "write_off":
                # v['transact_no'] = transact_no.rstrip(transact_no[-1]) + str(int(transact_no[-1])) + "-2"
                v['transact_no'] = FinanceService.make_unicode(str(transact_no))  # 流水号
                # v['finance_status_code'] = ""
                finance_transact, post_err = FinanceTransactService.post(v)
                if post_err:
                    return None, post_err
                # 生成真实记录成功后 原沙盒记录改为核销
                Transact.objects.filter(transact_no=transact_no).update(is_write_off=1, is_reverse=None)  # 沙盒核销
            elif type == "reverse":
                Transact.objects.filter(transact_no=transact_no).update(is_reverse=1, is_write_off=None)  # 沙盒红冲
            elif type == "cash_withdrawal":
                v['transact_no'] = FinanceService.make_unicode(str(order_no))  # 流水号
                finance_transact, post_err = FinanceTransactService.post(v)
                if post_err:
                    return None, post_err
                    # 生成真实记录成功后 原沙盒记录改为核销 并把提现状态改成 已提现
                Transact.objects.filter(transact_no=transact_no).update(is_write_off=1, sand_box_status_code="withdrew",
                                                                        is_reverse=None)  # 沙盒核销
            elif type == "transfered":

                v['transact_no'] = FinanceService.make_unicode(str(transact_no))  # 流水号
                # if not sys.modules.get("xj_enroll.service.enroll_services.EnrollServices"):
                #     from xj_enroll.service.enroll_services import EnrollServices
                #     pay_call_back_data, pay_call_back_err = EnrollServices.bxtx_pay_call_back(v['order_no'])
                #     if pay_call_back_err:
                #         logger.info(">>>>报名修改失败" + pay_call_back_err)
                #     else:
                #         finance_status_code = pay_call_back_data
                #         print(pay_call_back_data)
                # v['finance_status_code'] = finance_status_code
                v['finance_status_code'] = 232
                # v['images'] = images
                finance_transact, post_err = FinanceTransactService.post(v)
                if post_err:
                    return None, post_err
                # 生成真实记录成功后 原沙盒记录改为核销
                Transact.objects.filter(transact_no=transact_no).update(
                    finance_status_code=232,
                    sand_box_status_code="TRANSFERED",
                    is_write_off=1,
                    is_reverse=None)  # 沙盒核销
            elif type == "refuse":

                # v['transact_no'] = FinanceService.make_unicode(str(transact_no))  # 流水号
                v['images'] = images
                # 生成真实记录成功后 原沙盒记录改为核销
                Transact.objects.filter(transact_no=transact_no).update(
                    finance_status_code=615,
                    is_reverse=None)  # 沙盒核销

        if not err and type == "transfered":
            if not sys.modules.get("xj_enroll.service.enroll_services.EnrollServices"):
                from xj_enroll.service.enroll_services import EnrollServices
                pay_call_back_data, pay_call_back_err = EnrollServices.bxtx_pay_call_back(order_no)
                if pay_call_back_err:
                    logger.info(">>>>报名修改失败" + pay_call_back_err)
                else:
                    finance_status_code = pay_call_back_data
                    print(pay_call_back_data)

        return None, None

    @staticmethod
    def finance_create_or_write_off(data):
        data['action'] = "收入"
        finance_order, err_txt = FinanceTransactService.finance_flow_writing(params=data, finance_type='PAY')
        if finance_order:
            params = {"order_no": finance_order, "type": "write_off"}
            FinanceTransactsService.write_off(params)

        return None, None

    @staticmethod
    def cash_withdrawal(params):
        platform_set, err = UserPlatformService.payment_get_platform_info(params['platform_id'])
        if err:
            return None, err

        balance = FinanceService.check_balance(account_id=params['user_id'], platform=platform_set['platform_name'],
                                               # platform_id=None,
                                               currency='CNY',
                                               sand_box=None)
        if balance['balance'] < float(params['total_amount']):
            return None, "余额不足"
        params['total_fee'] = float("-" + params['total_amount'])
        params['pay_mode'] = 'BALANCE'

        # （用户余额应扣）
        finance_data = {
            "sand_box": sand_box_cash_withdrawal,  # 提现沙盒
            "order_no": FinanceService.make_unicode(str(params['user_id'])),
            "transact_no": FinanceService.make_unicode(str(params['user_id'])),
            "account_id": params['user_id'],
            "their_account_id": params['user_id'],
            "platform": platform_set['platform_name'],
            "amount": params['total_fee'],
            "currency": "CNY",
            "pay_mode": params['pay_mode'],
            "finance_status_code": 2,
            "sand_box_status_code": "withdrawing",
            "summary": "用户提现",

        }

        # # （平台应付）
        # platform_revenue_data = {
        #     "sand_box":sand_box_meet,
        #     "order_no": FinanceService.make_unicode(str(params['user_id'])),
        #     # their_account_name": sub_appid,
        #     "account_id": finance_data['their_account'],
        #     "their_account_id": params['user_id'],
        #     "platform": params['platform'],
        #     "amount": params['total_fee'],
        #     "summary": "用户提现",
        #     "currency": "CNY",
        #     "pay_mode": "BALANCE",
        #     "finance_status_code": 2
        # }
        finance_platform_data_set, finance_platform_err = FinanceTransactService.post(finance_data)
        if finance_platform_err:
            return None, finance_platform_err
            print(">>>>payment_logic_processing_err", finance_platform_err)
            logger.info(">>>>payment_logic_processing" + "写入资金模块失败（用户余额应扣）")
        return None, None

    @staticmethod
    def get_finance_thread(params, user_id):
        page = int(params['page']) - 1 if 'page' in params else 0
        size = int(params['size']) if 'size' in params else 10
        transact_list, err = FinanceTransactsService.get(params, user_id)
        if err:
            return None, err
        transact_list['list'] = filter_result_field(
            result_list=transact_list['list'],
            alias_dict={"snapshot": "snapshot"}
        )
        income = 0
        outgo = 0
        for i in transact_list['list']:
            income += float(i['income'])
            outgo += float(i['outgo'])

        statistics = {
            "income": income,
            "outgo": outgo,
        }
        thread_id_list = [item.get("thread_id", None) for item in transact_list['list']]
        # print("thread_id_list:", thread_id_list)
        thread_list, err = ThreadListService.search(thread_id_list)
        if err:
            return None, err
        # print("thread_list:", thread_list)
        data = JoinList(transact_list['list'], thread_list, "thread_id", "id").join()
        # print("data:", data)
        # print(thread_id_list)
        # total = transact.count()
        # return {'total': 0, 'list': data}, None
        return {'size': int(size), 'page': int(page + 1), 'total': transact_list['total'], 'list': data,
                "statistics": statistics}, None
        # return {'size': int(size), 'page': int(page + 1), 'total': total, 'list': thread_id_list}, None

    @staticmethod
    def invoicing_approval(params):
        finance_id = params.get("finance_id", None)
        goods_info = params.get("goods_info", None)
        if not finance_id:
            return None, "id不能为空"
        finance = Transact.objects.filter(id=finance_id)
        finance_data = finance.first()
        if not finance_data:
            return None, "数据不存在"
        finance_data = model_to_dict(finance_data)
        finance_goods_info = finance_data['goods_info']
        jsDumps = json.dumps(finance_goods_info)
        jsLoads = json.loads(jsDumps)
        for i in goods_info:
            before_key = i[0:i.rfind('__')]  # 截取指定字符前的字符串
            behind_key = i.split('__')[-1]  # 截取指定字符后的字符串
            if before_key in jsLoads:
                object = jsLoads[before_key]
                object[behind_key] = goods_info[i]
                jsLoads[before_key] = object
        # print(json.dumps(jsLoads))
        finance.update(sand_box_status_code="INVOICED", goods_info=jsLoads)
        enroll_list = []
        # if 'enroll' in jsLoads:
        #     for i in finance_goods_info['enroll']:
        #         enroll_list.append(i['id'])
        #     # enroll_list = FinanceTransactsService.get_json_primary_key(snapshot)
        #     if not sys.modules.get("xj_enroll.service.enroll_services.EnrollServices"):
        #         from xj_enroll.service.enroll_services import EnrollServices
        #     EnrollServices.enroll_edit(params={"finance_invoicing_code": "INVOICED"},
        #                                search_param={"enroll_id_list": enroll_list})
        if 'enroll' in jsLoads:
            if not sys.modules.get("xj_enroll.service.enroll_services.EnrollServices"):
                from xj_enroll.service.enroll_services import EnrollServices
            if isinstance(finance_goods_info['enroll'], dict):
                EnrollServices.enroll_edit(params={"finance_invoicing_code": "INVOICING"},
                                           search_param={"enroll_id": finance_goods_info['enroll']['id']})
            else:
                for i in finance_goods_info['enroll']:
                    enroll_list.append(int(i['id']))
                EnrollServices.enroll_edit(params={"finance_invoicing_code": "INVOICING"},
                                           search_param={"enroll_id_list": enroll_list})
        return None, None

    @staticmethod
    def large_transfer(params):
        # print(params)
        finance, err_txt = FinanceTransactService.finance_flow_writing(params=params, finance_type='TRANSFER')
        if err_txt:
            return None, err_txt
        return None, None

    @staticmethod
    def large_amount_audit(params):
        enroll_id = params.get("enroll_id", "")

        transact_set = Transact.objects.filter(enroll_id=enroll_id, sand_box_status_code="TRANSFERING").first()
        if transact_set:
            return {"status": "1"}, None
        else:
            return {"status": "0"}, None

    # @staticmethod
    # def get_json_primary_key(json):
    #     enroll_list = []
    #     for item in json:
    #         enroll_list.append(item['id'])
    #     return enroll_list

    @staticmethod
    def finance_standing_book(params):
        enroll_id_list = params.get("enroll_id_list", None)
        transact_obj = Transact.objects
        list = []
        for i in enroll_id_list:
            standing_book = {}
            standing_book['enroll_id'] = i  # 报名ID
            standing_book['billing_time'] = None  # 开票时间
            standing_book['charge_time'] = None  # 收款时间时间
            standing_book['charge_mode'] = None  # 收款方式
            standing_book['payment_time'] = None  # 付款时间 （暂无）
            standing_book['payment_delay'] = None  # 付款方式（暂无）
            standing_book['billing_time'] = None  # 开票时间

            transact_set = transact_obj.filter(enroll_id=i, sand_box__isnull=True, ).order_by("-id").first()
            if not transact_set:
                list.append(standing_book)
                continue

            finance_data = transact_set.to_dict()
            pay_mode = PayMode.objects.filter(id=finance_data['pay_mode']).first()
            pay_mode_data = model_to_dict(pay_mode)
            standing_book['charge_time'] = finance_data['transact_time']  # 收款时间时间
            standing_book['charge_mode'] = pay_mode_data['pay_mode']  # 收款方式

            invoice_set = transact_obj.filter(
                sand_box__sand_box_name__in=["BID_SPECIAL_INVOICE", "BID_PLAIN_INVOICE"]
            ).order_by("-id").values("goods_info")
            if not invoice_set:
                continue
            for item in (invoice_set):
                if item['goods_info']:
                    # jsDumps = json.dumps(goods_info, cls=DateEncoder)
                    # jsLoads = json.loads(jsDumps)
                    # print(jsLoads)
                    if "enroll" in item['goods_info']:
                        enroll = item['goods_info']['enroll']
                        if isinstance(enroll, dict):
                            if enroll["id"] == i:
                                if 'invoice' in item['goods_info']:
                                    invoice = item['goods_info']['invoice']
                                    billing_time = invoice.get("billing_time", None)
                                    standing_book['billing_time'] = billing_time
                        else:
                            for enroll_item in enroll:
                                if enroll_item["id"] == i:
                                    if 'invoice' in item['goods_info']:
                                        invoice = item['goods_info']['invoice']
                                        billing_time = invoice.get("billing_time", None)
                                        standing_book['billing_time'] = billing_time

                                        # print(standing_book)
            invoiced_amount = float(finance_data['income']) + float(finance_data['outgo'])
            standing_book['invoiced_amount'] = abs(invoiced_amount)  # 发票金额
            list.append(standing_book)

        return list, None
