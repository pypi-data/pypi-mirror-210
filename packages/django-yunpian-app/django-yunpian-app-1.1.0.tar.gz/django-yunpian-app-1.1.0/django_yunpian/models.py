# pylint: disable=unused-argument, no-member

"""
云片网的模型
"""

import math
import json
import logging

from django.db import models
from django.db.models.signals import post_save

from rest_framework.exceptions import Throttled
from yunpian_python_sdk.ypclient import YunpianClient

from . import exceptions


log = logging.getLogger(__name__)


class Account(models.Model):
    """云片网注册的帐号"""
    name = models.CharField("帐号名称", unique=True, max_length=63)
    apikey = models.CharField("APIKEY", unique=True, max_length=63)

    def __str__(self):
        return f"Account: {self.name}"

    @property
    def ypclient(self):
        return YunpianClient(self.apikey)


class Sign(models.Model):
    """签名"""
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    name = models.CharField("签名内容", max_length=31)

    def __str__(self):
        return f"Sign: {self.name}"


class Template(models.Model):
    """短信模板"""
    TYPE_CHOICE = (
        ("验证码类", "验证码类"),
        ("通知类", "通知类"),
        ("会员营销类", "会员营销类"),
    )
    id = models.IntegerField(unique=True, primary_key=True)
    sign = models.ForeignKey(Sign, on_delete=models.CASCADE)
    _type = models.CharField("短信类型", choices=TYPE_CHOICE, max_length=15)
    content = models.TextField(
        "模板内容", help_text="要是python的format形式.里面的变量用{}包裹")
    min_interval = models.IntegerField("最短间隔", default=0)

    def __str__(self):
        return f"{self.id}模板: {self.content}"


class Message(models.Model):
    """发送的短信记录"""
    STATUS_CHOICE = (
        ("发送成功", "发送成功"),
        ("发送中", "发送中"),
        ("发送失败", "发送失败"),
    )
    mobile = models.CharField("手机号", max_length=14)
    template = models.ForeignKey(
        Template, on_delete=models.SET_NULL, null=True)
    status = models.CharField(
        "状态", choices=STATUS_CHOICE, max_length=31, default="发送中")
    params = models.TextField(
        "短信参数", help_text="用json.dumps后的参数", default="{}")
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message: {self.id}"

    def _check_if_over_throt(self):
        """是否允许发送"""
        last_message = Message.objects.filter(
            mobile=self.mobile,
            template=self.template,
            status="发送成功",
        ).order_by("time").last()
        if last_message is None:
            return
        wait_time = math.ceil(
            self.template.min_interval - \
            (self.time - last_message.time).total_seconds()
        )
        if wait_time > 0:
            raise Throttled(wait_time)

    def send(self):
        """发送短信"""
        self._check_if_over_throt()
        ypclient = self.template.sign.account.ypclient
        params = json.loads(self.params)
        content = self.template.content.format(**params)
        text = f"【{self.template.sign.name}】{content}"
        r = ypclient.sms().single_send({
            "mobile": self.mobile,
            "text": text,
        })
        if r.code() == 0:
            self.status = "发送成功"
            self.save()
        else:
            self.status = "发送失败"
            self.save()
        if r.code() == 10:
            log.error(r.detail())
            log.error(self)
            raise exceptions.NoHarassException(r.detail())
        if r.code() != 0:
            log.error("短信发送失败")
            log.error(r.code())
            log.error(self)
            log.error(r)
            log.error(text)
            log.error(r.exception())
            raise exceptions.YunpianException(r.detail())

    @classmethod
    def post_save(cls, sender, *args, **kwargs):
        instance = kwargs["instance"]
        created = kwargs["created"]
        if created:
            instance.send()


post_save.connect(Message.post_save, sender=Message)
