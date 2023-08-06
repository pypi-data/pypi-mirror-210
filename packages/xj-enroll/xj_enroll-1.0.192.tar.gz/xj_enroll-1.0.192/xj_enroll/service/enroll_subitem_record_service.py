# encoding: utf-8
"""
@project: djangoModel->valuation_service
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis: 报名计时服务
@created_time: 2022/10/13 9:40
"""
from django.core.paginator import Paginator, EmptyPage
from django.db import transaction
from django.db.models import F

from xj_user.services.user_detail_info_service import DetailInfoService
from ..models import EnrollSubitemRecord, EnrollRecord, EnrollSubitem
from ..utils.custom_tool import format_params_handle, force_transform_type


class EnrollSubitemRecordService:

    @staticmethod
    def add(params: dict = None):
        params, is_pass = force_transform_type(variable=params, var_type="dict", default={})
        exclude_code, is_pass = force_transform_type(variable=params.get("exclude_code"), var_type="int", default=124)
        # ================ section 参数验证 start =====================
        try:
            # 参数类型校验
            params = format_params_handle(
                param_dict=params,
                is_validate_type=True,
                is_remove_empty=True,
                filter_filed_list=[
                    "enroll_record_id|int", "enroll_subitem_id|int", "user_id|int", "price|float", "count|int", "subitem_amount|float",
                    "enroll_subitem_status_code|int", "reply", "remark", "files|dict", "photos|dict"
                ],
            )
            # 参数必填验证
            must_key = ["enroll_record_id", "enroll_subitem_id", "user_id"]
            for k in must_key:
                if not params.get(k):
                    return None, "参数错误：" + k + "必填"
            # 报名记录与报名分项确认是否存在
            if not EnrollRecord.objects.filter(id=params.get("enroll_record_id")).first():
                return None, "不存在记录ID为" + str(params.get("enroll_record_id")) + "报名记录"
            subitem_obj = EnrollSubitem.objects.filter(id=params.get("enroll_subitem_id")).first()
            if not subitem_obj:
                return None, "不存在分项ID为" + str(params.get("enroll_subitem_id")) + "报名分项"
            # 防止重复添加
            if EnrollSubitemRecord.objects.filter(
                    enroll_record_id=params.get("enroll_record_id"),
                    enroll_subitem_id=params.get("enroll_subitem_id"),
                    user_id=params.get("user_id")
            ).exclude(enroll_subitem_status_code=exclude_code).first():
                return None, "已经生成分项记录，无需再次生成"
        except ValueError as e:
            return None, str(e)
        # ================ section 参数验证 end   =====================
        # IO操作
        try:
            instance = EnrollSubitemRecord.objects.create(**params)
            add_info = instance.to_json()
            return {"id": add_info.get("id"), "enroll_id": subitem_obj.enroll_id}, None
        except Exception as e:
            return None, str(e)

    @staticmethod
    def edit(params=None, pk=None):
        # ================ section 数据合法型验证 start =====================
        pk, is_pass = force_transform_type(variable=params.pop("id", pk), var_type="int")
        if not pk:
            return None, "不是有效的修改主键"

        # 检查是否存在该分项记录数据
        query_obj = EnrollSubitemRecord.objects.annotate(
            enroll_id=F("enroll_subitem__enroll_id")
        ).filter(id=pk).values("id", "enroll_id")
        if not query_obj:
            return None, "没有可修改的数据"

        # 流程合法型校验
        query_obj_first = query_obj.first()
        enroll_id, is_pass = force_transform_type(variable=params.pop("enroll_id", None), var_type="int")
        if enroll_id and not enroll_id == query_obj_first.get("enroll_id"):
            return None, "该报名(" + str(enroll_id) + ")不存在ID为(" + str(pk) + ")的分项记录"

        # 字段合法性校验, 禁止修改分项、记录、用户的ID
        try:
            params = format_params_handle(
                param_dict=params,
                is_remove_empty=True,
                is_validate_type=True,
                filter_filed_list=[
                    "price|float", "count|int", "subitem_amount|float",
                    "enroll_subitem_status_code|int", "reply", "remark", "files|dict", "photos|dict"
                ]
            )
        except ValueError as e:
            return None, str(e)
        # ================ section 数据合法型验证 end   =====================
        # IO操作
        try:
            EnrollSubitemRecord.objects.filter(id=pk).update(**params)
        except Exception as e:
            return None, "修改异常:" + str(e)
        return None, None

    @staticmethod
    def list(params, need_pagination=True):
        # 字段处理
        size = params.pop('size', 10)
        page = params.pop('page', 1)
        params['enroll_status_code'] = params['enroll_status_code'].split(";") if params.get("enroll_status_code") else None
        params = format_params_handle(
            param_dict=params,
            filter_filed_list=[
                "enroll_record_id", "enroll_record_id__in", "enroll_subitem_id", "enroll_subitem_id__in", "user_id", "price", "count", "subitem_amount",
                "enroll_subitem_status_code", "reply", "remark", "files", "photos", "enroll_id"
            ],
            alias_dict={"enroll_status_code": "enroll_status_code__in"}
        )
        # 全部展示
        query_obj = EnrollSubitemRecord.objects.annotate(enroll_id=F("enroll_record__enroll_id")).filter(**params).values()
        if not need_pagination:
            res_list = list(query_obj)
            # 拼接用户信息
            user_ids = [i["user_id"] for i in res_list]
            user_info_map = {i["user_id"]: i for i in DetailInfoService.get_list_detail(None, user_id_list=user_ids)}
            for j in res_list:
                j["user_info"] = user_info_map.get(j["user_id"], {})

            return res_list, None

        paginator = Paginator(query_obj, size)
        # 分页展示
        try:
            paginator_obj = paginator.page(page)
        except EmptyPage:
            return {'total': paginator.count, "page": page, "size": size, 'list': []}, None
        except Exception as e:
            print("e", e)
            return None, f'{str(e)}'
        # 拼接用户信息
        res_list = list(paginator_obj.object_list)
        user_ids = [i["user_id"] for i in res_list]
        user_info_map = {i["user_id"]: i for i in DetailInfoService.get_list_detail(None, user_id_list=user_ids)}
        for j in res_list:
            j["user_info"] = user_info_map.get(j["user_id"], {})

        return {'total': paginator.count, "page": page, "size": size, 'list': res_list}, None

    @staticmethod
    def delete(pk, search_params=None):
        """取消报名"""
        if not search_params:
            subrecord_obj = EnrollSubitemRecord.objects.filter(id=pk)
        else:
            try:
                subrecord_obj = EnrollSubitemRecord.objects.filter(**search_params)
            except Exception as e:
                return None, "搜索参数不正确"

        if not subrecord_obj:
            return None, "没有可修改得到数据"

        try:
            subrecord_obj.delete()
        except Exception as e:
            return None, "删除异常:" + str(e)
        return None, None

    @staticmethod
    def batch_copy(pk=None, copy_params=None, copy_num=None, ):
        """
        批量复制报名分项记录
        :param copy_params: 复制插入的参数
        :param pk: 搜索ID主键
        :param copy_count: 复制参数
        :return: data,err
        """
        if not copy_num:
            return None, "拷贝的分数不能为空，至少为1分"

        if not pk and not copy_params:
            return None, "找不到可以复制的记录"

        # 开始事务
        sid = transaction.savepoint()
        try:
            if not copy_params or isinstance(copy_params, dict):
                copy_params_obj = EnrollSubitemRecord.objects.filter(id=pk)
                if not copy_params_obj:
                    return None, "找不到可以复制的记录"
                copy_params = copy_params_obj.first().to_json()

            # 遍历插入数据
            for i in range(copy_num):
                EnrollSubitemRecord.objects.create(**copy_params)

            # 清除保存点
            transaction.clean_savepoints()
            return None, None

        except Exception as e:
            print("err:", str(e))
            transaction.savepoint_rollback(sid)
            return None, str(e)
