import ast

from django.views.decorators.http import require_http_methods
from rest_framework import response

from rest_framework.response import Response
from rest_framework.views import APIView

from utils.custom_tool import request_params_wrapper
from xj_captcha.services.sms_service import SmsService
from xj_captcha.utils.user_wrapper import user_authentication_wrapper
from ..utils.model_handle import parse_data
from ..utils.custom_response import util_response
from ..services.send_short_message_service import SendShortMessageService


class SmsApis(APIView):

    # 短信验证码发送
    @require_http_methods(['POST'])
    # @user_authentication_wrapper
    @request_params_wrapper
    def send(self, *args, request_params, **kwargs, ):
        params = request_params
        data, err_txt = SmsService.send_sms(params)
        if err_txt:
            return util_response(err=47767, msg=err_txt)
        return util_response(data=data)

    # 手机验证码检查
    @require_http_methods(['POST'])
    # @user_authentication_wrapper
    @request_params_wrapper
    def check(self, *args, request_params, **kwargs, ):
        params = request_params
        data, err_txt = SmsService.check_sms(params)
        if err_txt:
            return util_response(err=47767, msg=err_txt)
        return util_response(data=data)

    # 短信通知
    @require_http_methods(['POST'])
    @request_params_wrapper
    def bid_send_sms(self, *args, request_params, **kwargs, ):
        params = request_params
        data, err_txt = SmsService.bid_send_sms(params)
        if err_txt:
            return util_response(err=47767, msg=err_txt)
        return util_response(data=data)
