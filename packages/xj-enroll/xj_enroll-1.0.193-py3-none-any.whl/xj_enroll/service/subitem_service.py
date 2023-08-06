# encoding: utf-8
"""
@project: djangoModel->subitem_service
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis: 报名分项记录
@created_time: 2022/10/15 12:38
"""

from django.core.paginator import Paginator, EmptyPage
from django.db.models import F

from ..models import EnrollSubitem, EnrollSubitemExtendField, Enroll, EnrollSubitemRecord
from ..serializers import EnrollSubitemSerializer
from ..service.enroll_subitem_record_service import EnrollSubitemRecordService
from ..service.subitem_extend_service import input_convert, output_convert
from ..utils.custom_tool import format_params_handle, force_transform_type


class SubitemService:
    @staticmethod
    def add(params: dict = None, **kwargs):
        """
        分项添加
        :param params: 添加参数
        :return: None，err
        """
        params, is_pass = force_transform_type(variable=params, var_type="only_dict", default={})
        kwargs, is_pass = force_transform_type(variable=kwargs, var_type="only_dict", default={})
        params.update(kwargs)
        # ============= section 报名ID合法性判断 start ==================
        exclude_code, is_pass = force_transform_type(variable=params.get("exclude_code"), var_type="int")
        enroll_id, is_pass = force_transform_type(variable=params.get("enroll_id"), var_type="int")
        if not enroll_id:
            return None, "请填写报名ID"
        enroll_obj = Enroll.objects.filter(id=enroll_id)
        if exclude_code:
            enroll_obj = enroll_obj.exclude(enroll_status_code=exclude_code)
        enroll_info = enroll_obj.first()
        if not enroll_info:
            return None, "报名不存在"
        # ============= section 报名ID合法性判断 end   ==================

        # ============= section 参数处理 start ==================
        params = input_convert(
            params_dict=params,
            enroll_id=enroll_id
        )
        try:
            params = format_params_handle(
                param_dict=params,
                is_validate_type=True,
                is_remove_empty=True,
                filter_filed_list=[
                    "enroll_id|int",
                    "name",
                    "price|float",
                    "count|int",
                    "unit",
                    "amount|float",
                    "enroll_subitem_status_code|int",
                    "description",
                    "remark",
                    "field_1",
                    "field_2",
                    "field_3",
                    "field_4",
                    "field_5",
                    "field_6",
                    "field_7",
                    "field_8",
                    "field_9",
                    "field_10",
                ]
            )
        except ValueError as e:
            return None, str(e)
        # ============= section 参数处理 end ==================
        try:
            instance = EnrollSubitem.objects.create(**params)
            add_info = instance.to_json()
            return {"enroll_id": enroll_id, "id": add_info.get("id")}, None
        except Exception as e:
            return None, str(e)

    @staticmethod
    def edit(params: dict = None, subitem_id=None):
        # 参数验证
        params, is_pass = force_transform_type(variable=params, var_type="only_dict", default={})
        subitem_id, is_pass = force_transform_type(variable=params.pop("id", subitem_id), var_type="int", default=0)
        subitem_obj_first = EnrollSubitem.objects.filter(id=subitem_id).first()
        if not subitem_obj_first:
            return None, "找不到ID为" + str(subitem_id) + "的数据"
        subitem_info = subitem_obj_first.to_json()

        # 流程验证，同时剔除报名ID。报名分项不允许更改报名ID。
        enroll_id, is_pass = force_transform_type(variable=params.pop("enroll_id", None), var_type="int")  # 流程控制得到报名ID
        if enroll_id and not enroll_id == subitem_info.get("enroll_id"):
            return None, "报名ID不可修改，报名ID为(" + str(enroll_id) + ")的报名不存在ID为(" + str(subitem_id) + ")的分项"

        # ============= section 参数处理 start ==================
        params = input_convert(
            params_dict=params,
            enroll_id=subitem_info.get("enroll_id")
        )
        try:
            params = format_params_handle(
                param_dict=params,
                is_validate_type=True,
                is_remove_empty=True,
                filter_filed_list=[
                    "name",
                    "price|float",
                    "count|int",
                    "unit",
                    "amount|float",
                    "enroll_subitem_status_code|int",
                    "description",
                    "remark",
                    "field_1",
                    "field_2",
                    "field_3",
                    "field_4",
                    "field_5",
                    "field_6",
                    "field_7",
                    "field_8",
                    "field_9",
                    "field_10",
                ]
            )
        except ValueError as e:
            return None, str(e)
        # ============= section 参数处理 end ==================

        # 开始修改
        try:
            EnrollSubitem.objects.filter(id=subitem_id).update(**params)
        except Exception as e:
            return None, "修改异常:" + str(e)

        # 联动修改全部报名相关得到状态，迁移到报名服务中，通过流程控制
        # unfinish_count = EnrollSubitem.objects.filter(enroll_id=enroll_id).exclude(enroll_subitem_status_code=668).exclude(enroll_subitem_status_code=124).count()
        # if unfinish_count == 0 and enroll_id:
        #     EnrollStatusCodeService.batch_edit_code(enroll_id, params.get("enroll_subitem_status_code", 668))
        #     try:
        #         # ============ 完成订单联动资金修改 start ============
        #         # TODO 资金联动代码块，后期使用流程控制
        #         commision = Enroll.objects.filter(id=enroll_id).values("commision").first()
        #         commision = commision.get("commision") if commision else 0
        #         records_vales = list(EnrollRecord.objects.filter(enroll_id=enroll_id,enroll_status_code=668).values("user_id", "price", "initiator_again_price"))
        #         for item in records_vales:
        #             write_to_log(prefix="资金联动修改：", content={
        #                 "account_id": item.get("user_id"),
        #                 "amount": commision or 0,
        #                 "currency": "CNY",
        #                 "pay_mode": "BALANCE",
        #                 "enroll_id": enroll_id
        #             })
        #             FinanceTransactsService.finance_create_or_write_off(data={
        #                 "account_id": item.get("user_id"),
        #                 "amount": commision or 0,
        #                 "currency": "CNY",
        #                 "pay_mode": "BALANCE",
        #                 "enroll_id": enroll_id
        #             })
        #         # ============ 完成订单联动资金修改 end ============
        #     except Exception as e:
        #         write_to_log(prefix="资金联动修改：", err_obj=e)
        return None, None

    @staticmethod
    def detail(pk=None):
        # 参数验证
        subitem_obj = EnrollSubitem.objects.annotate(category_id=F("enroll__category_id")).filter(id=pk).first()
        if not subitem_obj:
            return None, "找不到ID为" + str(pk) + "的数据"

        subitem_dict = EnrollSubitemSerializer(subitem_obj, many=False).data
        subitem_list = output_convert([subitem_dict])
        subitem_detail = subitem_list[0] if subitem_list else {}

        subitem_detail["subitem_record_list"] = list(EnrollSubitemRecord.objects.filter(enroll_subitem_id=pk).values())
        return subitem_detail, None

    @staticmethod
    def list(params: dict = None, is_pagination=True):
        params, is_pass = force_transform_type(variable=params, var_type="dict", default={})
        is_pagination, is_pass = force_transform_type(variable=is_pagination, var_type="bool", default=True)
        size, is_pass = force_transform_type(variable=params.pop('size', 10), var_type="int", default=10)
        page, is_pass = force_transform_type(variable=params.pop('page', 1), var_type="int", default=1)
        # 字段过滤
        params = format_params_handle(
            param_dict=params,
            is_remove_empty=True,
            filter_filed_list=[
                "id|int", "category_id|int", "enroll_subitem_status_code|int", "enroll_subitem_status_codes|list_int",
                "enroll_id|int", "name", "price|float", "count|int", "unit", "description", "remark"
            ],
            split_list=["enroll_subitem_status_codes"],
            alias_dict={"name": "name__contains", "enroll_subitem_status_codes": "enroll_subitem_status_code__in"}
        )
        try:
            # 不分页查询
            fetch_obj = EnrollSubitem.objects.annotate(category_id=F("enroll__category_id")).filter(**params).values()
            total = fetch_obj.count()
            if not is_pagination and total <= 2000:
                result_list = output_convert(list(fetch_obj))
                # 拼接分项记录
                subitem_ids = [i["id"] for i in result_list]
                res_list, err = EnrollSubitemRecordService.list({"enroll_subitem_id__in": subitem_ids}, False)
                subitem_record_map = {}
                for item in res_list:
                    if subitem_record_map.get(item["enroll_subitem_id"]):
                        subitem_record_map[item["enroll_subitem_id"]].append(item)
                    else:
                        subitem_record_map[item["enroll_subitem_id"]] = [item]
                for item in result_list:
                    item["subitem_record_list"] = subitem_record_map.get(item.get("id"))
                return result_list, None
            else:
                # 分页查询
                paginator = Paginator(fetch_obj, size)
                try:
                    page_obj = paginator.page(page)
                except EmptyPage:
                    return {'total': total, "page": page, "size": size, 'list': []}, None
                result_list = list(page_obj.object_list)
                result_list = output_convert(result_list)
                # 拼接分项记录
                subitem_ids = [i["id"] for i in result_list]
                res_list, err = EnrollSubitemRecordService.list({"enroll_subitem_id__in": subitem_ids}, False)
                subitem_record_map = {}
                for item in res_list:
                    if subitem_record_map.get(item["enroll_subitem_id"]):
                        subitem_record_map[item["enroll_subitem_id"]].append(item)
                    else:
                        subitem_record_map[item["enroll_subitem_id"]] = [item]
                return {'total': total, "size": size, 'page': page, 'list': result_list}, None
        except Exception as e:
            return [], str(e)

    # 批量修改
    @staticmethod
    def batch_edit(params, enroll_id=None):
        enroll_id = enroll_id or params.pop("enroll_id", None)
        if not enroll_id:
            return None, "请填写报名ID"

        # 参数根据类别转化
        params = input_convert(
            params_dict=params,
            enroll_id=enroll_id
        )
        if not params:
            return None, "enroll_id不能为空，或者参数为空"

        subitem_enroll_obj = EnrollSubitem.objects.filter(enroll_id=enroll_id)
        if not subitem_enroll_obj:
            return None, "没有找到enroll_id为" + str(enroll_id) + "的报名分项"
        try:
            subitem_enroll_obj.update(**params)
        except Exception as e:
            return None, "修改参数错误:" + str(e)
        return None, None

    @staticmethod
    def delete(subitem_rule_id):
        subitem_enroll_obj = EnrollSubitem.objects.filter(id=subitem_rule_id)
        if not subitem_enroll_obj:
            return None, None
        try:
            subitem_enroll_obj.delete()
        except Exception as e:
            return None, "删除异常:" + str(e)
        return None, None

    @staticmethod
    def extend_field(params=None, is_pagination=True):
        validate_params = params if isinstance(params, dict) else {}

        size = validate_params.pop('size', 10)
        page = validate_params.pop('page', 1)

        filtered_params = format_params_handle(
            param_dict=validate_params,
            filter_filed_list=["id", "category_id", "field_index", "field", "label", "type", "config", "description", ],
            alias_dict={"field": "field__contains", "label": "label__contains"}
        )

        try:
            extend_obj = EnrollSubitemExtendField.objects.all()
            extend_obj_list = extend_obj.filter(**filtered_params).values()
            if not is_pagination:
                return list(extend_obj_list), None

            paginator = Paginator(extend_obj_list, size)
            paginator_obj_list = paginator.page(page)
            data = {'total': paginator.count, "size": size, 'page': page, 'list': list(paginator_obj_list.object_list)}
            return data, None
        except Exception as e:
            return [], "查询参数错误：" + str(e)

    @staticmethod
    def check_num(enroll_id):
        enroll_obj = Enroll.objects.filter(id=enroll_id).first()
        if not enroll_obj:
            return False
        enroll_count = enroll_obj.to_json().get("count")
        subitem_count = EnrollSubitem.objects.filter(enroll_id=enroll_id).count()
        if enroll_count > subitem_count:
            return True
        return False
