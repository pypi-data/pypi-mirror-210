# _*_coding:utf-8_*_
from django.urls import re_path

from xj_finance.apis.finance_currency_apis import FinanceCurrencyApi
from xj_finance.apis.finance_pay_mode import FinancePayMode
from xj_finance.apis.finance_pay_mode_apis import FinancePayModeApi
from xj_finance.apis.finance_sand_box_apis import FinanceSandBoxApi
from xj_finance.apis.finance_status_code_apis import FinanceStatusCodeApis
from .apis.finance_apis import FinanceApi
from .apis.finance_transacts import FinanceTransacts
from .apis.finance_transact import FinanceTransact
from .apis.finance_currency import FinanceCurrency
from .apis.finance_sand_box import FinanceSandBox
from .apis.finance_statistic import FinanceStatistic
from .apis.finance_status_code import FinanceStatusCode

urlpatterns = [
    re_path(r'^statistic/?$', FinanceStatistic.as_view(), ),

    # 财务总表
    re_path(r'^transacts/?$', FinanceApi.list, ),  # 财务交易列表(旧)
    re_path(r'^transact/?$', FinanceApi.detail, ),  # 财务交详细(旧)

    re_path(r'^list/?$', FinanceApi.list, ),  # 财务交详细(新命名)
    re_path(r'^detail/?$', FinanceApi.detail, ),  # 财务交详细(新命名)
    re_path(r'^add/?$', FinanceApi.add, ),  # 财务交易添加
    re_path(r'^edit/?$', FinanceApi.edit, ),  # 财务交易修改
    re_path(r'^balance/?$', FinanceApi.balance, ),  # 获取余额
    re_path(r'^cash_withdrawal/?$', FinanceApi.cash_withdrawal, ),  # 财务提现
    re_path(r'^large_transfer/?$', FinanceApi.large_transfer, ),  # 大额转账
    re_path(r'^examine_approve/?$', FinanceApi.examine_approve, ),  # 财务审批

    # 财务币种表
    re_path(r'^currency/?$', FinanceCurrency.as_view(), ),  # 币种|列表（旧）

    re_path(r'^currency_list/?$', FinanceCurrencyApi.list, ),  # 币种列表
    re_path(r'^currency_add/?$', FinanceCurrencyApi.add, ),  # 币种添加
    re_path(r'^currency_edit/?$', FinanceCurrencyApi.edit, ),  # 币种修改

    # 财务支付方式表

    re_path(r'^pay_mode/?$', FinancePayMode.as_view(), ),

    re_path(r'^pay_mode_list/?$', FinancePayModeApi.list, ),  # 支付方式列表
    re_path(r'^pay_mode_add/?$', FinancePayModeApi.add, ),  # 支付方式添加
    re_path(r'^pay_mode_edit/?$', FinancePayModeApi.edit, ),  # 支付方式修改

    # 财务沙盒表
    re_path(r'^sand_box/?$', FinanceSandBox.as_view(), ),

    re_path(r'^sand_box_list/?$', FinanceSandBoxApi.list, ),  # 沙盒列表
    re_path(r'^sand_box_add/?$', FinanceSandBoxApi.add, ),  # 沙盒添加
    re_path(r'^sand_box_edit/?$', FinanceSandBoxApi.edit, ),  # 沙盒修改

    re_path(r'^write_off/?$', FinanceTransacts.large_transfer, ),
    re_path(r'^large_amount_audit/?$', FinanceTransacts.large_amount_audit, ),
    re_path(r'^invoicing_approval/?$', FinanceTransacts.invoicing_approval, ),
    re_path(r'^create_or_write_off/?$', FinanceTransacts.create_or_write_off, ),  # 服务 财务交易应收应付

    re_path(r'^flow_writing/?$', FinanceTransact.finance_flow_writing, ),

    re_path(r'^status_code/?$', FinanceStatusCode.as_view(), ),

    re_path(r'^status_code_list/?$', FinanceStatusCodeApis.list, ),  # 付款类型列表
    re_path(r'^status_code_add/?$', FinanceStatusCodeApis.add, ),  # 付款类型添加
    re_path(r'^status_code_edit/?$', FinanceStatusCodeApis.edit, ),  # 付款类型修改

    re_path(r'^standing_book/?$', FinanceTransact.finance_standing_book, ),  # 资金台账
    re_path(r'^balance_validation/?$', FinanceTransact.balance_validation, ),

    # re_path(r'^extend_field_list/?$', ThreadExtendFieldList.as_view(), name='extend_field_list'),  # 展示类型列表
    # 该功能已使用finance_transact的POST方法代替

]
