import io
import json
import datetime

from django.shortcuts import HttpResponse, redirect, render

from web.forms.account import SendMsgForm, RegisterForm, LoginForm
from web import models

from backend import commons
from backend.utils import check_code as CheckCode
from backend.utils.response import BaseResponse

def register(request):
    """
    注册
    :param request:
    :return:
    """
    rep = BaseResponse()
    form = RegisterForm(request.POST)
    if form.is_valid():
        current_date = datetime.datetime.now()
        limit_day = current_date - datetime.timedelta(minutes=1)
        _value_dict = form.clean()

        is_valid_code = models.SendMsg.objects.filter(email=_value_dict['email'],
                                                      code=_value_dict['email_code'],
                                                      ctime=limit_day).count()

        if not is_valid_code:
            rep.message['email_code']= "邮箱验证码不正确或过期"
            return HttpResponse(json.dumps(rep.__dict__))

        has_exists_email = models.UserInfo.objects.filter(email=_value_dict['email']).count()

        if has_exists_email:
            rep.message['email'] = '邮箱已存在'
            return HttpResponse(json.dump(rep.__dict__))

        has_exists_username = models.UserInfo.objects.filter()
        if has_exists_username:
            rep.message['email'] = '用户名已存在'
            return HttpResponse(json.dumps(rep.__dict__))

        _value_dict['ctime'] = current_date
        _value_dict.pop('email_code')
        #当前用户的所有信息
        obj = models.UserInfo.objects.create(**_value_dict)

        user_info_dict = {'nid': obj.nid, 'email': obj.email, 'username': obj.username}

        models.SendMsg.objects.filter(email=_value_dict['email']).delete()

        request.session['is_login'] = True
        request.session['user_info'] = user_info_dict
        rep.status = True

    else:
        # error_msg = form.error.as_json()
        # rep.message = json.loads(error_msg)
        rep.summary = form.errors['email'][0]
    return HttpResponse(json.dumps(rep.__dict__))


