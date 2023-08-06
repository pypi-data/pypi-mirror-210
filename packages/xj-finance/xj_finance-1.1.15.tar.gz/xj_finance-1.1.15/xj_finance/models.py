from django.db import models
import time


class PayMode(models.Model):
    pay_mode = models.CharField(verbose_name='支付方式编码 ', max_length=128)
    pay_value = models.CharField(verbose_name='支付方式 ', max_length=128)

    # description = models.CharField(verbose_name='描述 ', max_length=128) # sieyoo准备加

    class Meta:
        db_table = 'finance_pay_mode'
        verbose_name_plural = "4. 财务 - 支付方式"

    def __str__(self):
        return f"{self.pay_mode}"


class Currency(models.Model):
    currency = models.CharField(verbose_name='币种 ', max_length=128)

    # description = models.CharField(verbose_name='描述 ', max_length=128) # sieyoo准备加

    class Meta:
        db_table = 'finance_currency'
        verbose_name_plural = "6. 财务 - 币种列表"

    def __str__(self):
        return f"{self.currency}"


class SandBox(models.Model):
    id = models.AutoField(verbose_name='ID', primary_key=True)
    sand_box_name = models.CharField(verbose_name='沙盒名称', max_length=128)
    sand_box_label = models.CharField(verbose_name='沙盒标签', max_length=128)
    description = models.CharField(verbose_name='描述', max_length=128)
    config = models.JSONField(verbose_name='前端配置')

    class Meta:
        db_table = 'finance_sandbox'
        verbose_name_plural = "7. 财务 - 沙盒列表"

    def __str__(self):
        return f"{self.sand_box_name}"


# 生成交易号：2位数（当前年份后2位数字）+8位数（当前时间戳去头2位）+6位数（用户名 经过hash crc16生成的 4位十六进制 转成5位数 然后头为补0）

# 2位数（当前年份后2位数字）+8位数（当前时间戳去头2位）
def year_timestamp():
    date_time = time.localtime(time.time())
    # 截取第3位到第4位
    year_str = (str(date_time.tm_year))[2:4]
    # 当前时间戳
    time_stamp = str(int(time.time()))
    # 截取第3位到第10位
    eight_time_stamp = time_stamp[2:10]
    code = year_str + eight_time_stamp
    return code


# crc16
# @brief 传入需要编码一致性的字符串
# @return 返回十六进制字符串
def make_crc16(self):
    a = 0xFFFF
    b = 0xA001
    for byte in self:
        a ^= ord(byte)
        for i in range(8):
            last = a % 2
            a >>= 1
            if last == 1:
                a ^= b
    s = hex(a).upper()
    return s[2:6]


class Transact(models.Model):
    # year_timestamp函数+hash算法
    hex_code = make_crc16('admin')
    decimal_code = int(hex_code, 16)
    zero_code = '0' + str(decimal_code)
    create_transact_id = year_timestamp() + zero_code

    platform_id = models.IntegerField(verbose_name='平台ID', blank=False, null=False, help_text='')
    thread_id = models.IntegerField(verbose_name='信息ID', blank=False, null=False, help_text='')
    transact_no = models.CharField(verbose_name='交易号', unique=True, max_length=255, blank=True, db_index=True)
    enroll_id = models.IntegerField(verbose_name='报名ID', blank=False, null=False, help_text='')
    enroll_record_id = models.IntegerField(verbose_name='报名详情ID', blank=False, null=False, help_text='')
    order_no = models.CharField(verbose_name='平台订单号', db_index=True, max_length=255, blank=True)
    account_id = models.IntegerField(verbose_name='账户ID', blank=False, null=False, help_text='')
    their_account_id = models.IntegerField(verbose_name='对方账户ID', blank=False, null=False, help_text='')
    transact_time = models.DateTimeField(verbose_name='交易时间', auto_now_add=True)
    summary = models.CharField(verbose_name='摘要说明', max_length=255, blank=True, null=True)
    currency = models.ForeignKey(verbose_name='币种', to=Currency, db_column='currency_id', related_name='+',
                                 on_delete=models.DO_NOTHING, default=1, unique=False, blank=True, null=True,
                                 db_constraint=False,
                                 help_text='')
    pay_mode = models.ForeignKey(verbose_name='支付方式', to=PayMode, db_column='pay_mode_id', on_delete=models.DO_NOTHING,
                                 db_constraint=False,
                                 unique=False, blank=True, null=True, default=5)
    opposite_account = models.CharField(verbose_name='对方科目', blank=True, null=True, max_length=255, )
    income = models.DecimalField(verbose_name='收入', max_digits=32, decimal_places=8, blank=True, null=True)
    outgo = models.DecimalField(verbose_name='支出', max_digits=32, decimal_places=8, blank=True, null=True)
    balance = models.DecimalField(verbose_name='余额', max_digits=32, decimal_places=8, default=0)
    goods_info = models.JSONField(verbose_name='商品信息', blank=True, null=True)
    pay_info = models.JSONField(verbose_name='付款信息', blank=True, null=True)
    remark = models.TextField(verbose_name='备注', blank=True, null=True)
    images = models.CharField(verbose_name='多图上传', blank=True, null=True, max_length=1000)
    sand_box = models.ForeignKey(verbose_name='沙盒', to=SandBox, db_column='sand_box_id', related_name='+',
                                 on_delete=models.DO_NOTHING, unique=False, blank=True, null=True, db_index=True,
                                 db_constraint=False, )
    finance_status_code = models.CharField(verbose_name='资金状态码', default='', max_length=32, blank=True, null=True)
    is_reverse = models.BooleanField(verbose_name='是否红冲', blank=True, null=True)
    is_delete = models.BooleanField(verbose_name='是否删除', blank=True, null=True)
    is_write_off = models.BooleanField(verbose_name='是否核销', max_length=255, blank=True, null=True)
    sand_box_status_code = models.CharField(verbose_name='沙盒状态码', max_length=32, blank=True, null=True)
    bookkeeping_type = models.CharField(verbose_name='记账类型', blank=True, null=True, max_length=32)

    class Meta:
        db_table = 'finance_transact'
        verbose_name_plural = "1. 财务 - 交易明细"

    def to_dict(self):
        """重写model_to_dict()方法转字典"""
        from datetime import datetime

        opts = self._meta
        data = {}
        for f in opts.concrete_fields:
            value = f.value_from_object(self)
            if isinstance(value, datetime):
                value = value.strftime('%Y-%m-%d %H:%M:%S')
            elif isinstance(f, models.FileField):
                value = value.url if value else None
            data[f.name] = value
        return data
    # 起作用 https://docs.djangoproject.com/zh-hans/3.2/ref/contrib/admin/#django.contrib.admin.ModelAdmin.list_display
    # @admin.display(description='啥')
    # def transact_time(self):
    #     # return self.transact_time.strftime('%Y-%m-%d %I:%M:%S')
    #     return '测'

    # “反向” 关联
    # 若模型有ForeignKey，外键关联的模型实例将能访问Manager，后者会返回第一个模型的所有实例。默认情况下，该Manager名为FOO_set， FOO即源模型名的小写形式。 Manager返回QuerySets，后者能以 “检索对象” 章节介绍的方式进行筛选和操作。
    # 你可以在定义ForeignKey时设置related_name参数重写这个FOO_set名。例如，若修改Entry模型为blog = ForeignKey(Blog, on_delete=models.CASCADE, related_name='entries')，前文示例代码会看起来像这样:


class FinanceExtendData(models.Model):
    """ 5、Finance_FinanceExtendData 扩展字段数据表 """

    class Meta:
        db_table = 'finance_extend_data'
        verbose_name_plural = '05. 扩展字段数据表'

    finance_id = models.OneToOneField(verbose_name='财务ID', to=Transact, related_name="finance_extend_data",
                                      db_column='finance_id',
                                      primary_key=True, on_delete=models.DO_NOTHING, help_text='')
    field_1 = models.CharField(verbose_name='自定义字段_1', max_length=255, blank=True, null=True, help_text='')
    field_2 = models.CharField(verbose_name='自定义字段_2', max_length=255, blank=True, null=True, help_text='')
    field_3 = models.CharField(verbose_name='自定义字段_3', max_length=255, blank=True, null=True, help_text='')
    field_4 = models.CharField(verbose_name='自定义字段_4', max_length=255, blank=True, null=True, help_text='')
    field_5 = models.CharField(verbose_name='自定义字段_5', max_length=255, blank=True, null=True, help_text='')
    field_6 = models.CharField(verbose_name='自定义字段_6', max_length=255, blank=True, null=True, help_text='')
    field_7 = models.CharField(verbose_name='自定义字段_7', max_length=255, blank=True, null=True, help_text='')
    field_8 = models.CharField(verbose_name='自定义字段_8', max_length=255, blank=True, null=True, help_text='')
    field_9 = models.CharField(verbose_name='自定义字段_9', max_length=255, blank=True, null=True, help_text='')
    field_10 = models.CharField(verbose_name='自定义字段_10', max_length=255, blank=True, null=True, help_text='')
    field_11 = models.CharField(verbose_name='自定义字段_11', max_length=255, blank=True, null=True, help_text='')
    field_12 = models.CharField(verbose_name='自定义字段_12', max_length=255, blank=True, null=True, help_text='')
    field_13 = models.CharField(verbose_name='自定义字段_13', max_length=255, blank=True, null=True, help_text='')
    field_14 = models.CharField(verbose_name='自定义字段_14', max_length=255, blank=True, null=True, help_text='')
    field_15 = models.CharField(verbose_name='自定义字段_15', max_length=255, blank=True, null=True, help_text='')
    field_16 = models.CharField(verbose_name='自定义字段_16', max_length=255, blank=True, null=True, help_text='')
    field_17 = models.CharField(verbose_name='自定义字段_17', max_length=255, blank=True, null=True, help_text='')
    field_18 = models.CharField(verbose_name='自定义字段_18', max_length=255, blank=True, null=True, help_text='')
    field_19 = models.CharField(verbose_name='自定义字段_19', max_length=255, blank=True, null=True, help_text='')
    field_20 = models.CharField(verbose_name='自定义字段_20', max_length=255, blank=True, null=True, help_text='')
    field_21 = models.CharField(verbose_name='自定义字段_21', max_length=255, blank=True, null=True, help_text='')
    field_22 = models.CharField(verbose_name='自定义字段_22', max_length=255, blank=True, null=True, help_text='')
    field_23 = models.CharField(verbose_name='自定义字段_23', max_length=255, blank=True, null=True, help_text='')
    field_24 = models.CharField(verbose_name='自定义字段_24', max_length=255, blank=True, null=True, help_text='')
    field_25 = models.CharField(verbose_name='自定义字段_25', max_length=255, blank=True, null=True, help_text='')
    field_26 = models.CharField(verbose_name='自定义字段_26', max_length=255, blank=True, null=True, help_text='')
    field_27 = models.CharField(verbose_name='自定义字段_27', max_length=255, blank=True, null=True, help_text='')
    field_28 = models.CharField(verbose_name='自定义字段_28', max_length=255, blank=True, null=True, help_text='')
    field_29 = models.CharField(verbose_name='自定义字段_29', max_length=255, blank=True, null=True, help_text='')
    field_30 = models.CharField(verbose_name='自定义字段_30', max_length=255, blank=True, null=True, help_text='')
    field_31 = models.CharField(verbose_name='自定义字段_31', max_length=255, blank=True, null=True, help_text='')
    field_32 = models.CharField(verbose_name='自定义字段_32', max_length=255, blank=True, null=True, help_text='')
    field_33 = models.CharField(verbose_name='自定义字段_33', max_length=255, blank=True, null=True, help_text='')
    field_34 = models.CharField(verbose_name='自定义字段_34', max_length=255, blank=True, null=True, help_text='')
    field_35 = models.CharField(verbose_name='自定义字段_35', max_length=255, blank=True, null=True, help_text='')
    field_36 = models.CharField(verbose_name='自定义字段_36', max_length=255, blank=True, null=True, help_text='')
    field_37 = models.CharField(verbose_name='自定义字段_37', max_length=255, blank=True, null=True, help_text='')
    field_38 = models.CharField(verbose_name='自定义字段_38', max_length=255, blank=True, null=True, help_text='')
    field_39 = models.CharField(verbose_name='自定义字段_39', max_length=255, blank=True, null=True, help_text='')
    field_40 = models.CharField(verbose_name='自定义字段_40', max_length=255, blank=True, null=True, help_text='')

    def __str__(self):
        return f"{self.finance_id}"

    def short_field_1(self):
        if self.field_1 and len(self.field_1) > 25:
            return f"{self.field_1[0:25]}..."
        return self.field_1

    short_field_1.short_description = '自定义字段1'

    def short_field_2(self):
        if self.field_2 and len(self.field_2) > 25:
            return f"{self.field_2[0:25]}..."
        return self.field_2

    short_field_2.short_description = '自定义字段2'

    def short_field_3(self):
        if self.field_3 and len(self.field_3) > 25:
            return f"{self.field_3[0:25]}..."
        return self.field_3

    short_field_3.short_description = '自定义字段3'

    def short_field_4(self):
        if self.field_4 and len(self.field_4) > 25:
            return f"{self.field_4[0:25]}..."
        return self.field_4

    short_field_4.short_description = '自定义字段4'

    def short_field_5(self):
        if self.field_5 and len(self.field_5) > 25:
            return f"{self.field_5[0:25]}..."
        return self.field_5

    short_field_5.short_description = '自定义字段5'

    def short_field_6(self):
        if self.field_6 and len(self.field_6) > 25:
            return f"{self.field_6[0:25]}..."
        return self.field_6

    short_field_6.short_description = '自定义字段6'

    def short_field_7(self):
        if self.field_7 and len(self.field_7) > 25:
            return f"{self.field_7[0:25]}..."
        return self.field_7

    short_field_7.short_description = '自定义字段7'

    def short_field_8(self):
        if self.field_8 and len(self.field_8) > 25:
            return f"{self.field_8[0:25]}..."
        return self.field_8

    short_field_8.short_description = '自定义字段8'

    def short_field_9(self):
        if self.field_9 and len(self.field_9) > 25:
            return f"{self.field_9[0:25]}..."
        return self.field_9

    short_field_9.short_description = '自定义字段9'

    def short_field_10(self):
        if self.field_10 and len(self.field_10) > 25:
            return f"{self.field_10[0:25]}..."
        return self.field_10

    short_field_10.short_description = '自定义字段10'

    def short_field_11(self):
        if self.field_11 and len(self.field_11) > 25:
            return f"{self.field_11[0:25]}..."
        return self.field_11

    short_field_11.short_description = '自定义字段11'

    def short_field_12(self):
        if self.field_12 and len(self.field_12) > 25:
            return f"{self.field_12[0:25]}..."
        return self.field_12

    short_field_12.short_description = '自定义字段12'

    def short_field_13(self):
        if self.field_13 and len(self.field_13) > 25:
            return f"{self.field_13[0:25]}..."
        return self.field_13

    short_field_13.short_description = '自定义字段13'

    def short_field_14(self):
        if self.field_14 and len(self.field_14) > 25:
            return f"{self.field_14[0:25]}..."
        return self.field_14

    short_field_14.short_description = '自定义字段14'

    def short_field_15(self):
        if self.field_15 and len(self.field_15) > 25:
            return f"{self.field_15[0:25]}..."
        return self.field_15

    short_field_15.short_description = '自定义字段15'

    def short_field_16(self):
        if self.field_16 and len(self.field_16) > 25:
            return f"{self.field_16[0:25]}..."
        return self.field_16

    short_field_16.short_description = '自定义字段16'

    def short_field_17(self):
        if self.field_17 and len(self.field_17) > 25:
            return f"{self.field_17[0:25]}..."
        return self.field_17

    short_field_17.short_description = '自定义字段17'

    def short_field_18(self):
        if self.field_18 and len(self.field_18) > 25:
            return f"{self.field_18[0:25]}..."
        return self.field_18

    short_field_18.short_description = '自定义字段18'

    def short_field_19(self):
        if self.field_19 and len(self.field_19) > 25:
            return f"{self.field_19[0:25]}..."
        return self.field_19

    short_field_19.short_description = '自定义字段19'

    def short_field_20(self):
        if self.field_20 and len(self.field_20) > 25:
            return f"{self.field_20[0:25]}..."
        return self.field_20

    short_field_20.short_description = '自定义字段20'

    def short_field_21(self):
        if self.field_21 and len(self.field_21) > 25:
            return f"{self.field_21[0:25]}..."
        return self.field_21

    short_field_21.short_description = '自定义字段21'

    def short_field_22(self):
        if self.field_22 and len(self.field_22) > 25:
            return f"{self.field_22[0:25]}..."
        return self.field_22

    short_field_22.short_description = '自定义字段22'

    def short_field_23(self):
        if self.field_23 and len(self.field_23) > 25:
            return f"{self.field_23[0:25]}..."
        return self.field_23

    short_field_23.short_description = '自定义字段23'

    def short_field_24(self):
        if self.field_24 and len(self.field_24) > 25:
            return f"{self.field_24[0:25]}..."
        return self.field_24

    short_field_24.short_description = '自定义字段24'

    def short_field_25(self):
        if self.field_25 and len(self.field_25) > 25:
            return f"{self.field_25[0:25]}..."
        return self.field_25

    short_field_25.short_description = '自定义字段25'

    def short_field_26(self):
        if self.field_26 and len(self.field_26) > 25:
            return f"{self.field_26[0:25]}..."
        return self.field_26

    short_field_26.short_description = '自定义字段26'

    def short_field_27(self):
        if self.field_27 and len(self.field_27) > 25:
            return f"{self.field_27[0:25]}..."
        return self.field_27

    short_field_27.short_description = '自定义字段27'

    def short_field_28(self):
        if self.field_28 and len(self.field_28) > 25:
            return f"{self.field_28[0:25]}..."
        return self.field_28

    short_field_28.short_description = '自定义字段28'

    def short_field_29(self):
        if self.field_29 and len(self.field_29) > 25:
            return f"{self.field_29[0:25]}..."
        return self.field_29

    short_field_29.short_description = '自定义字段29'

    def short_field_30(self):
        if self.field_30 and len(self.field_30) > 25:
            return f"{self.field_30[0:25]}..."
        return self.field_30

    short_field_30.short_description = '自定义字段30'

    def short_field_31(self):
        if self.field_31 and len(self.field_31) > 25:
            return f"{self.field_31[0:25]}..."
        return self.field_31

    short_field_31.short_description = '自定义字段31'

    def short_field_32(self):
        if self.field_32 and len(self.field_32) > 25:
            return f"{self.field_32[0:25]}..."
        return self.field_32

    short_field_32.short_description = '自定义字段32'

    def short_field_33(self):
        if self.field_33 and len(self.field_33) > 25:
            return f"{self.field_33[0:25]}..."
        return self.field_33

    short_field_33.short_description = '自定义字段33'

    def short_field_34(self):
        if self.field_34 and len(self.field_34) > 25:
            return f"{self.field_34[0:25]}..."
        return self.field_34

    short_field_34.short_description = '自定义字段34'

    def short_field_35(self):
        if self.field_35 and len(self.field_35) > 25:
            return f"{self.field_35[0:25]}..."
        return self.field_35

    short_field_35.short_description = '自定义字段35'

    def short_field_36(self):
        if self.field_36 and len(self.field_36) > 25:
            return f"{self.field_36[0:25]}..."
        return self.field_36

    short_field_36.short_description = '自定义字段36'

    def short_field_37(self):
        if self.field_37 and len(self.field_37) > 25:
            return f"{self.field_37[0:25]}..."
        return self.field_37

    short_field_37.short_description = '自定义字段37'

    def short_field_38(self):
        if self.field_38 and len(self.field_38) > 25:
            return f"{self.field_38[0:25]}..."
        return self.field_38

    short_field_38.short_description = '自定义字段38'

    def short_field_39(self):
        if self.field_39 and len(self.field_39) > 25:
            return f"{self.field_39[0:25]}..."
        return self.field_39

    short_field_39.short_description = '自定义字段39'

    def short_field_40(self):
        if self.field_40 and len(self.field_40) > 25:
            return f"{self.field_40[0:25]}..."
        return self.field_40

    short_field_40.short_description = '自定义字段40'


# 扩展字段表。用于声明扩展字段数据表中的(有序)字段具体对应的什么键名。注意：扩展字段是对分类的扩展，而不是主类别的扩展
class FinanceExtendField(models.Model):
    """  6、FinanceExtendField 扩展字段表 """

    class Meta:
        db_table = 'finance_extend_field'
        verbose_name_plural = '09. 财务 - 扩展字段表'
        ordering = ['-sand_box_id']

    field_index_choices = [
        ("field_1", "field_1"),
        ("field_2", "field_2"),
        ("field_3", "field_3"),
        ("field_4", "field_4"),
        ("field_5", "field_5"),
        ("field_6", "field_6"),
        ("field_7", "field_7"),
        ("field_8", "field_8"),
        ("field_9", "field_9"),
        ("field_10", "field_10"),
        ("field_11", "field_11"),
        ("field_12", "field_12"),
        ("field_13", "field_13"),
        ("field_14", "field_14"),
        ("field_15", "field_15"),
        ("field_16", "field_16"),
        ("field_17", "field_17"),
        ("field_18", "field_18"),
        ("field_19", "field_19"),
        ("field_20", "field_20"),
        ("field_21", "field_21"),
        ("field_22", "field_22"),
        ("field_23", "field_23"),
        ("field_24", "field_24"),
        ("field_25", "field_25"),
        ("field_26", "field_26"),
        ("field_27", "field_27"),
        ("field_28", "field_28"),
        ("field_29", "field_29"),
        ("field_30", "field_30"),
        ("field_31", "field_31"),
        ("field_32", "field_32"),
        ("field_33", "field_33"),
        ("field_34", "field_34"),
        ("field_35", "field_35"),
        ("field_36", "field_36"),
        ("field_37", "field_37"),
        ("field_38", "field_38"),
        ("field_39", "field_39"),
        ("field_40", "field_40"),
    ]
    type_choices = [
        ("string", "string"),
        ("int", "int"),
        ("float", "float"),
        ("bool", "bool"),
        ("select", "select"),
        ("radio", "radio"),
        ("checkbox", "checkbox"),
        ("date", "date",),
        ("time", "time",),
        ("datetime", "datetime"),
        ("moon", "moon"),
        ("year", "year"),
        ("color", "color"),
        ("file", "file"),
        ("image", "image"),
        ("switch", "switch"),
        ("cascader", "cascader"),
        ("plain", "plain"),
        ("textarea", "textarea"),
        ("text", "text"),
        ("number", "number"),
        ("upload", "upload"),
        ("password", "password"),
    ]

    id = models.AutoField(verbose_name='ID', primary_key=True, help_text='')
    # 数据库生成classify_id字段
    sand_box = models.ForeignKey(verbose_name='沙盒ID', null=True, blank=True, to=SandBox,
                                 db_column='sand_box_id', related_name='+', on_delete=models.DO_NOTHING, help_text='')
    field = models.CharField(verbose_name='自定义字段', max_length=255, help_text='')  # 眏射ThreadExtendData表的键名
    field_index = models.CharField(verbose_name='冗余字段', max_length=255, help_text='',
                                   choices=field_index_choices)  # 眏射ThreadExtendData表的键名
    value = models.CharField(verbose_name='字段介绍', max_length=255, null=True, blank=True, help_text='')
    type = models.CharField(verbose_name='字段类型', max_length=255, blank=True, null=True, choices=type_choices,
                            help_text='')
    unit = models.CharField(verbose_name='参数单位', max_length=255, blank=True, null=True, help_text='')
    config = models.JSONField(verbose_name='字段配置', blank=True, null=True, default=dict, help_text='')
    description = models.CharField(verbose_name='数据配置', max_length=255, blank=True, null=True, default=dict,
                                   help_text='')
    default = models.CharField(verbose_name='默认值', max_length=2048, blank=True, null=True, help_text='')

    def __str__(self):
        return f"{self.id}"


class StatusCode(models.Model):
    id = models.AutoField(verbose_name='ID', primary_key=True)
    finance_status_code = models.CharField(verbose_name='资金状态码', max_length=128)
    finance_status_name = models.CharField(verbose_name='资金状态名', max_length=128)
    description = models.CharField(verbose_name='描述', max_length=128)

    class Meta:
        db_table = 'finance_status_code'
        verbose_name_plural = "8. 财务 - 资金状态码表"

    def __str__(self):
        return f"{self.finance_status_code}"
