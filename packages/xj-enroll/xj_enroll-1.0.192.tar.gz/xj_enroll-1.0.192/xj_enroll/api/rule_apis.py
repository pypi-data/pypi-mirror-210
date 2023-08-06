# encoding: utf-8
"""
@project: djangoModel->rule_api
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis:  计价 规则API
@created_time: 2022/9/20 13:20
"""
from rest_framework.decorators import api_view
from rest_framework.views import APIView

from ..service.rule_service import RuleValueService
from ..utils.custom_response import util_response
from ..utils.custom_tool import parse_data, request_params_wrapper
from ..utils.user_wrapper import user_authentication_force_wrapper
from ..validator.rule_validator import RuleValidator


class RuleAPI(APIView):
    @api_view(['GET'])
    def list(self, *args, **kwargs, ):
        params = parse_data(self)
        need_pagination = params.get("need_pagination", 1)
        need_pagination = int(need_pagination)
        data, err = RuleValueService.list(params=params, need_pagination=need_pagination)
        if err:
            return util_response(err=1000, msg=err)
        return util_response(data=data)

    @api_view(['POST'])
    @user_authentication_force_wrapper
    def add(self, *args, **kwargs, ):
        params = parse_data(self)
        # 表单数据验证
        is_valid, error = RuleValidator(params).validate()
        if not is_valid:
            return util_response(err=1000, msg=error)
        # 添加数据
        data, err = RuleValueService.add(params)
        if err:
            return util_response(err=1001, msg=err)
        return util_response(data=data)

    @api_view(['PUT'])
    @user_authentication_force_wrapper
    def edit(self, *args, **kwargs, ):
        params = parse_data(self)
        rule_value_id = kwargs.get("rule_value_id") or params.pop("rule_value_id") or None
        if not rule_value_id:
            return util_response(err=1000, msg="参数错误:enroll_id不可以为空")
        data, err = RuleValueService.edit(params, rule_value_id)
        if err:
            return util_response(err=1000, msg=err)
        return util_response(data=data)

    @api_view(['DELETE'])
    @user_authentication_force_wrapper
    def delete(self, *args, **kwargs, ):
        params = parse_data(self)
        rule_value_id = kwargs.get("rule_value_id") or params.pop("rule_value_id") or None
        if not rule_value_id:
            return util_response(err=1000, msg="参数错误:enroll_id不可以为空")
        data, err = RuleValueService.edit(params, rule_value_id)
        if err:
            return util_response(err=1000, msg=err)
        return util_response(data=data)

    # 规则分组列表
    @request_params_wrapper
    def group_list(self, *args, request_params, **kwargs):
        data, err = RuleValueService.group_list(request_params)
        if err:
            return util_response(err=1000, msg=err)
        return util_response(data=data)
