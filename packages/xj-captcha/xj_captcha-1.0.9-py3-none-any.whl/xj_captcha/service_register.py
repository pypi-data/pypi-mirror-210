# encoding: utf-8
"""
@project: djangoModel->service_register
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis: 对外开放服务调用注册白名单
@created_time: 2023/1/12 14:29
"""

import xj_captcha
from .services import sms_service

# 对外服务白名单
register_list = [
    {
        # 短信通知接入
        "service_name": "bid_send_sms",
        "pointer": sms_service.SmsService.bid_send_sms
    },

]


# 遍历注册
def register():
    for i in register_list:
        setattr(xj_captcha, i["service_name"], i["pointer"])


if __name__ == '__main__':
    register()
