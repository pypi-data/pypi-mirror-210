import ast

from rest_framework import response

from rest_framework.response import Response
from rest_framework.views import APIView

from ..utils.model_handle import parse_data
from ..utils.custom_response import util_response
from ..services.send_short_message_service import SendShortMessageService


class SendShortMessag(APIView):
    def post(self, request):
        phone = self.request.data.get('phone', None)
        platform = self.request.data.get('platform', None)
        # phone = request.POST.get('phone')  # 获取手机号
        # platform = request.POST.get('platform')  # 获取短信平台
        # 4 发短信
        data, err_txt = SendShortMessageService.send_sms(phone, platform)
        if not data:
            return util_response(err=4002, msg=err_txt)
        return Response({
            'err': 0,
            'msg': 'OK',
            'data': data
        })
