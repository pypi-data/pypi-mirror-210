import re
from django.db import models
from django.apps import apps
from django.conf import settings


class BaseModel(models.Model):
    """基础的模型类,为其他表补存字段"""
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    is_delete = models.BooleanField(default=False, null=True, blank=True)

    class Meta:
        abstract = True


def model_field_relation(app_name, model_name):
    """返回模型类对象信息
    app_name : 模型类models所在的文件夹的名称 str
    model_nam : 模型类的名称 str
                如 ’User‘ 不是db_table
                如果通过对象获取使用 User.__name__ 会得到字符串 “User”
                model_obj._meta 可以获取 Meta的属性信息
    return (<django.db.models.fields.BigAutoField: id>, <django.db.models.fields.DateTimeField: create_time>)
    """
    model_obj = apps.get_model(app_name, model_name)
    filed = model_obj._meta.fields
    return filed


def name_attribute_relation(app_name, model_name, attribute_name='verbose_name', reverse=False):
    """
    :param app_name : 模型类models所在的文件夹的名称 str
    :param model_name : 模型类的名称 str
    :param attribute_name:  创建表字段的属性 如 verbose_name help_text max_length 等
    :param reverse: k v 互换
    :return:
        reverse=False
        {'id': 'ID', 'create_time': '创建时间', 'update_time': '更新时间', 'is_delete': 'is delete', 'tb_key': '字段名称', 'tb_value': '结果', 'tb_date': '时间', 'year_q': '年度季度标识', 'company_code': '公司编号'}
    """
    ret = {i.name: getattr(i, attribute_name) for i in model_field_relation(app_name, model_name)}
    if reverse:
        ret = {v: k for k, v in ret.items()}
    return ret


class AllModelDesc(object):
    """
    全部的表的解释说明
        all_desc
    单个字段的解释说明
    model_default
    model_choice
    model_type
    name_attribute_relation(参数attribute_name控制)
    """

    tables = ['default', 'verbose_name', 'help_text', 'null', 'choice', 'type']

    def model_default(self, app_name, model_name, attribute_name='default'):
        """
        默认值 没有就传空
        """
        ret_dcit = {}
        for i in model_field_relation(app_name, model_name):
            v = getattr(i, attribute_name)
            if isinstance(v, type):
                v = None
            ret_dcit[i.name] = v
        return ret_dcit

    def model_choice(self, app_name, model_name):
        """
        选项 没有为 []
        verbose_name： choices
        :return: {'gender': ['男', '女'], }
        """
        choice_dict = {}
        params = model_field_relation(app_name, model_name)
        for i in params:

            choices = i.choices
            if choices:
                choices = [i[0] for i in choices]
            else:
                choices = []
            choice_dict[i.name] = choices  # 'name': i.name,
        return choice_dict

    def model_type(self, app_name, model_name):
        """
        数据的类型
            数据库的类型转换
            Big Int 转int
            Text   转 str
        'name'： type
        :return: {'id': 'Integer', 'name': 'string'}
        """
        type_dict = {}
        params = model_field_relation(app_name, model_name)
        for i in params:
            tp = i.description
            tp = tp._proxy____args
            v = tp[0].split(' ')[0]
            if v == 'Big':
                v = 'Integer'
            elif v == 'Text':
                v = 'String'
            type_dict[i.name] = v

        return type_dict

    def all_desc(self, app_name, model_name):
        """
        输出如下

        key      默认值            中文             类型                下拉选项       不传          备注
        {'id': {'default': None, 'chinese': 'ID', 'type': 'Integer', 'choice': [], 'no': False, 'desc': ''},
        'NA': {'default': None, 'chinese': '科目名称', 'type': 'String', 'choice': [], 'no': False, 'desc': ''},
        'F': {'default': '借', 'chinese': '方向', 'type': 'String', 'choice': ['借', '贷'], 'no': False, 'desc': ''},
        'OUTNA': {'default': None, 'chinese': '报出科目', 'type': 'String', 'choice': [], 'no': True, 'desc': '注: 报出数据时如果不改变科目代码，不需要录入'}}

        """
        default_ = self.model_default(app_name, model_name)
        chinese_ = name_attribute_relation(app_name, model_name, attribute_name='verbose_name')
        type_ = self.model_type(app_name, model_name)
        choice_ = self.model_choice(app_name, model_name)
        desc_ = name_attribute_relation(app_name, model_name, attribute_name='help_text')
        no_ = name_attribute_relation(app_name, model_name, attribute_name='null')

        return {i: {'default': default_[i],
                    'chinese': chinese_[i],
                    'type': type_[i],
                    'choice': choice_[i],
                    'no': no_[i],
                    'desc': desc_[i]} for i in default_}


def show_model_class_name(fp):
    """显示.py 文件下面所有的 class名称"""
    # fp = os.path.abspath('..' + '/backstage/apps/admins/models.py')
    data = []
    with open(fp, 'r', encoding='utf-8') as f:
        while True:
            ret = f.readline()
            if not ret:
                break
            if re.search(r'class .*\):$', ret):
                data.append(ret.split(' ')[1].split('(')[0])
    return data


def get_user_model():
    """
    返回django settings配置中的用户模型类对象
    """
    try:
        return apps.get_model(settings.AUTH_USER_MODEL, require_ready=False)
    except ValueError:
        raise ValueError("AUTH_USER_MODEL must be of the form 'app_label.model_name'")


def get_user_obj(app_name, model_name):
    """
    返回model的obj
    app_name : 模型类models所在的文件夹的名称 str
    model_nam : 模型类的名称 str
    """
    model_obj = apps.get_model(app_name, model_name)
    return model_obj

