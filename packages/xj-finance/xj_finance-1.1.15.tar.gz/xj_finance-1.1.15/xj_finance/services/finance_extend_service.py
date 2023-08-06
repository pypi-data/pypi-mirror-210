# encoding: utf-8
"""
@project: djangoModel->extend_service
@author:高栋天
@Email: sky4834@163.com
@synopsis: 扩展服务
@created_time: 2022/7/29 15:14
"""
from django.db.models import F

from ..models import FinanceExtendField, Transact, FinanceExtendData
from ..utils.custom_tool import write_to_log, force_transform_type, filter_result_field, format_params_handle


# 扩展字段增删改查
class FianceExtendService:
    @staticmethod
    def create_or_update(params=None, finance_id=None, sand_box_id=None, **kwargs):
        """
        信息表扩展信息新增或者修改
        :param params: 扩展信息，必填
        :param finance_id: 财务ID，必填
        :param sand_box_id: 沙盒ID, 非必填
        :return: None，err
        """
        # 参数合并，强制类型转换
        kwargs, is_void = force_transform_type(variable=kwargs, var_type="dict", default={})
        params, is_void = force_transform_type(variable=params, var_type="dict", default={})
        params.update(kwargs)

        # 不存在信息ID 无法修改
        finance_id = finance_id or params.pop("finance_id", None)
        finance_id, is_void = force_transform_type(variable=finance_id, var_type="int")
        if finance_id is None:
            return None, "扩展字段修改错误,finance_id不可以为空"

        # 检查信息ID 是否正确
        Transact_obj = Transact.objects.filter(id=finance_id).first()
        if not Transact_obj:
            return None, "没有找到该主表信息，无法添加扩展信息"
        # 获取沙盒类别ID 当没有指定沙盒分类的时候，则不可以添加或者修改扩展数据。因为扩展字段于沙盒绑定。
        sand_box_id = sand_box_id if sand_box_id else Transact_obj.sand_box_id
        if not sand_box_id:
            return None, "没有信息指定砂灰色类别，无法添加扩展信息"

        # 扩展字段映射, 如没有配置对应类别的扩展字段，则无法添加扩展数据。
        extend_fields = FinanceExtendField.objects.filter(sand_box_id=sand_box_id).values("field_index", "default",
                                                                                          "field")
        if not extend_fields:
            return None, "没有配置扩展该类别的扩展字段，无法添加扩展信息"

        extend_model_fields = [i.name for i in FinanceExtendData._meta.fields if
                               not i.name == "finance_id"]  # 扩展信息表的字段列表
        # 扩展数据替换
        extend_field_map = {item["field"]: item["field_index"] for item in extend_fields if
                            item["field_index"] in extend_model_fields}  # 得到合理的配置
        transformed_extend_params = {extend_field_map[k]: v for k, v in params.items() if
                                     extend_field_map.get(k)}  # {"自定义扩展字段":"123"} ==>> {"filed_1":"123"}
        # 修改或添加数据
        try:
            extend_obj = FinanceExtendData.objects.filter(finance_id=finance_id)
            if not extend_obj:
                # 新增的时候，启用扩展字段参数设置默认值。
                # 注意：防止后台管理员配置错误,出现数据表不存在的字段。所以需要进行一次字段排除
                default_field_map = {item["field_index"]: item["default"] for item in extend_fields if
                                     (item["default"] and item["field_index"] in extend_model_fields)}
                for field_index, default in default_field_map.items():
                    transformed_extend_params.setdefault(field_index, default)
                if not transformed_extend_params:
                    return None, "没有可添加的数据，请检查扩展字段的默认值配置"

                # 添加扩展信息
                transformed_extend_params.setdefault('finance_id_id', finance_id)
                FinanceExtendData.objects.create(**transformed_extend_params)
                return None, None
            else:
                if not transformed_extend_params:
                    return None, "没有可修改的数据"

                extend_obj.update(**transformed_extend_params)
                return None, None
        except Exception as e:
            write_to_log(prefix="信息表扩展信息新增或者修改异常", err_obj=e)
            return None, "信息表扩展信息新增或者修改异常:" + str(e)

    @staticmethod
    def get_extend_info(finance_id_list: list = None):
        """
        获取映射后的扩展数据
        :param finance_id_list: 财务ID列表
        :return: extend_list, err
        """
        # 参数类型校验
        finance_id_list, is_void = force_transform_type(variable=finance_id_list, var_type="list")
        if not finance_id_list:
            return [], None

        # 信息与类别映射
        Transact_sand_box_list = list(Transact.objects.filter(id__in=finance_id_list).values("id", "sand_box_id"))
        Transact_sand_box_map = {i["id"]: i["sand_box_id"] for i in Transact_sand_box_list if
                                 i.get("sand_box_id", None)}

        # 扩展字段映射, 如没有配置对应类别的扩展字段，则无法添加扩展数据。
        extend_fields = list(FinanceExtendField.objects.values("sand_box_id", "field_index", "field"))
        if not extend_fields:
            return [], None
        extend_field_map = {}
        for item in extend_fields:
            if extend_field_map.get(item["sand_box_id"]):
                extend_field_map[item["sand_box_id"]].update({item["field_index"]: item["field"]})
            else:
                extend_field_map[item["sand_box_id"]] = {item["field_index"]: item["field"],
                                                         "finance_id_id": "finance_id"}
        # 查询出扩展原始数据
        try:
            Transact_extend_list = list(FinanceExtendData.objects.filter(finance_id__in=finance_id_list).values())
        except Exception as e:
            return [], "获取扩展数据异常"
        # 处理获取到结果，字段替换
        try:
            finish_list = []
            for i in Transact_extend_list:
                # 查看该条信息是否指定sand_box_id，没有则跳过
                current_sand_box_id = Transact_sand_box_map.get(i["finance_id_id"], None)
                if not current_sand_box_id:
                    continue
                # 如果该类别没有配置扩展字段则跳过
                current_extend_fields = extend_field_map.get(current_sand_box_id, {})
                if not current_extend_fields:
                    continue
                # 进行替换
                finish_list.append(format_params_handle(
                    param_dict=i,
                    alias_dict=current_extend_fields,
                    is_remove_null=False
                ))
            # 剔除不需要的字段
            finish_list = filter_result_field(
                result_list=finish_list,
                remove_filed_list=[i.name for i in FinanceExtendData._meta.fields if not i.name == "finance_id"]
            )
            return finish_list, None

        except Exception as e:
            write_to_log(prefix="获取映射后的扩展数据,数据拼接异常", err_obj=e, content="finance_id_list:" + str(finance_id_list))
            return [], None
