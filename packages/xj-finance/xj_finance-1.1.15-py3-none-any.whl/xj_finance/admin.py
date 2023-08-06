from django.contrib import admin

# 引入用户平台
from .models import PayMode, Currency, Transact, SandBox, StatusCode, FinanceExtendField


# Register your models here.


class PayModeAdmin(admin.ModelAdmin):
    fields = ('id', 'pay_mode', "pay_value")
    list_display = ('id', 'pay_mode', "pay_value")
    search_fields = ('id', 'pay_mode' "pay_value",)
    readonly_fields = ['id']


class CurrencyAdmin(admin.ModelAdmin):
    fields = ('id', 'currency',)
    list_display = ('id', 'currency',)
    search_fields = ('id', 'currency',)
    readonly_fields = ['id']


class SandBoxAdmin(admin.ModelAdmin):
    fields = ('id', 'sand_box_name', 'sand_box_label', 'description', 'config')
    list_display = ('id', 'sand_box_name', 'sand_box_label', 'description', 'config')
    search_fields = ('id', 'sand_box_name', 'sand_box_label', 'description', 'config')
    readonly_fields = ['id']


class StatusCodeAdmin(admin.ModelAdmin):
    fields = ('id', 'finance_status_code', 'finance_status_name', 'description',)
    list_display = ('id', 'finance_status_code', 'finance_status_name', 'description',)
    search_fields = ('id', 'finance_status_code', 'finance_status_name', 'description',)
    readonly_fields = ['id']


class TransactAdmin(admin.ModelAdmin):
    fields = ('id', 'platform', 'thread', 'transact_no', 'enroll', 'enroll_record', 'order_no',
              'account', 'their_account', 'transact_time', 'summary', 'currency', 'pay_mode', 'opposite_account',
              'income',
              'outgo',
              'balance', 'goods_info', 'pay_info', 'remark', 'images', 'sand_box', 'finance_status_code',
              'is_reverse', 'is_delete', 'is_write_off', 'sand_box_status_code', 'bookkeeping_type',)
    list_display = ('id', 'platform_id', 'thread_id', 'transact_no', 'enroll_id', 'enroll_record_id', 'order_no',
                    'account_id', 'their_account_id', 'transact_time', 'summary', 'currency_id', 'pay_mode_id',
                    'opposite_account',
                    'income',
                    'outgo',
                    'balance', 'goods_info', 'pay_info', 'remark', 'images', 'sand_box_id', 'finance_status_code',
                    'is_reverse', 'is_delete', 'is_write_off', 'sand_box_status_code', 'bookkeeping_type',)
    search_fields = (
        'id', 'account', 'their_account', 'transact_no', 'thread_id', 'enroll_id', 'transact_time', 'platform_id',
        'order_no',)
    # list_filter = ['platform', 'currency', 'account', 'their_account', 'order_no']
    readonly_fields = ['id', 'transact_time']
    # def platform(self, obj):
    #     return obj.platform

    # 不起作用 https://docs.djangoproject.com/zh-hans/3.2/ref/contrib/admin/#django.contrib.admin.ModelAdmin.list_display
    # @admin.display(description='Name')
    # def transact_time(self, obj):
    #     return "2424"


class EextendFieldAdmin(admin.ModelAdmin):
    fields = ('id', 'sand_box', 'field_index', 'field', 'value', 'type', 'unit', 'config', 'description', 'default')
    list_display = (
        'id', 'sand_box', 'field_index', 'field', 'value', 'type', 'unit', 'config', 'description', 'default')
    search_fields = (
        'id', 'sand_box', 'field_index', 'field', 'value', 'type', 'unit', 'config', 'description', 'default')
    readonly_fields = ['id']


admin.site.register(Transact, TransactAdmin)
admin.site.register(PayMode, PayModeAdmin)
admin.site.register(Currency, CurrencyAdmin)
admin.site.register(SandBox, SandBoxAdmin)
admin.site.register(StatusCode, StatusCodeAdmin)
admin.site.register(FinanceExtendField, EextendFieldAdmin)
