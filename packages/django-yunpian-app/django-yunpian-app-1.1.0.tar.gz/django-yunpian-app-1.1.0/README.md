# django-yunpian-app
继承了云片的app. 里面有各种适应云片网的model

# 安装
```
pip install django-yunpian-app
```

# 基础引入
1. 编辑`<your_project>/settings.py`
```
INSTALLED_APPS = [
    ...
    "django_yunpian"
    ...
]
```

2. 创建数据库表
```
python manage.py migrate
```

3. 根据自己的数据,创建账号,签名
```
from django_yunpian.models import Account, Sign, Template
account = Account.objects.create(
    ...
)
sign = Sign.objects.create(
    account=account,
    ...
)
template = Template.objects.create(
    sign=sign
    ...
)
```

4. 发送短信
```
from django_yunpian.models import Message
Message.objects.create(
    template = template,
    ...
)
```
