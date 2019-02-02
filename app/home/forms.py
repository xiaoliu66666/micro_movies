from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired
from wtforms import StringField, PasswordField, SubmitField, FileField, TextAreaField
from wtforms.fields.html5 import EmailField

from wtforms.validators import DataRequired, ValidationError, EqualTo, Email, Regexp

from app.models import User


class RegisterForm(FlaskForm):
    """
    注册表单
    """
    name = StringField(
        label="<span class='glyphicon glyphicon-user'></span> 昵称",
        validators=[
            DataRequired("请输入昵称！")
        ],
        description="昵称",
        render_kw={
            "class": "form-control input-lg",
            "placeholder": "请输入昵称！",
            "autofocus": "autofocus"
        }
    )
    email = EmailField(
        label="<span class='glyphicon glyphicon-envelope'></span> 邮箱",
        validators=[
            DataRequired("请输入邮箱！"),
            Email("邮箱不符合规范！")
        ],
        description="邮箱",
        render_kw={
            "class": "form-control input-lg",
            "placeholder": "请输入邮箱！"
        }
    )
    phone = StringField(
        label="<span class='glyphicon glyphicon-phone'></span> 手机",
        validators=[
            DataRequired("请输入手机！"),
            Regexp("^1[35678]\d{9}$", message="手机格式不正确！")
        ],
        description="手机",
        render_kw={
            "class": "form-control input-lg",
            "placeholder": "请输入手机！"
        }
    )
    pwd = PasswordField(
        label="<span class='glyphicon glyphicon-lock'></span> 密码",
        validators=[
            DataRequired("请输入密码！")
        ],
        description="密码",
        render_kw={
            "class": "form-control input-lg",
            "placeholder": "请输入密码！"
        }
    )
    pwd2 = PasswordField(
        label="<span class='glyphicon glyphicon-lock'></span> 确认密码",
        validators=[
            DataRequired("请确认密码！"),
            EqualTo("pwd", "两次密码不一致，请重新输入！")
        ],
        description="确认密码",
        render_kw={
            "class": "form-control input-lg",
            "placeholder": "请确认密码！"
        }
    )
    submit = SubmitField(
        '注册',
        render_kw={
            "class": "btn btn-lg btn-success btn-block",
        }
    )

    def validate_name(self, field):
        name = field.data
        user_cnt = User.query.filter_by(name=name).count()
        if user_cnt == 1:
            raise ValidationError("账号已存在，请重新输入！")

    def validate_email(self, field):
        email = field.data
        email_cnt = User.query.filter_by(email=email).count()
        if email_cnt == 1:
            raise ValidationError("手机号已存在，请重新输入！")

    def validate_phone(self, field):
        phone = field.data
        phone_cnt = User.query.filter_by(phone=phone).count()
        if phone_cnt == 1:
            raise ValidationError("邮箱已存在，请重新输入！")


class LoginForm(FlaskForm):
    """
    登录表单
    """
    name = StringField(
        label="<span class='glyphicon glyphicon-user'></span> 账号",
        validators=[
            DataRequired("请输入用户名！")
        ],
        description="账号",
        render_kw={
            "class": "form-control input-lg",
            "placeholder": "请输入用户名！",
            "autofocus": "autofocus"
        }
    )
    pwd = PasswordField(
        label="<span class='glyphicon glyphicon-lock'></span> 密码",
        validators=[
            DataRequired("请输入密码！")
        ],
        description="密码",
        render_kw={
            "class": "form-control input-lg",
            "placeholder": "请输入密码！"
        }
    )
    submit = SubmitField(
        '登录',
        render_kw={
            "class": "btn btn-lg btn-primary btn-block",
        }
    )

    def validate_name(self, filed):
        name = filed.data
        user_cnt = User.query.filter_by(name=name).count()
        if user_cnt == 0:
            raise ValidationError("账号不存在！")


class UserForm(FlaskForm):
    """
    用户表单
    """
    name = StringField(
        label="<span class='glyphicon glyphicon-user'></span>昵称",
        validators=[
            DataRequired("请输入昵称！")
        ],
        description="昵称",
        render_kw={
            "class": "form-control",
            "placeholder": "昵称",
            "autofocus": "autofocus"
        }
    )
    email = EmailField(
        label="<span class='glyphicon glyphicon-envelope'></span>邮箱",
        validators=[
            DataRequired("请输入邮箱！"),
            Email("邮箱不符合规范！")
        ],
        description="邮箱",
        render_kw={
            "class": "form-control",
            "placeholder": "邮箱"
        }
    )
    phone = StringField(
        label="<span class='glyphicon glyphicon-phone'></span>手机",
        validators=[
            DataRequired("请输入手机！"),
            Regexp("^1[35678]\d{9}$", message="手机格式不正确！")
        ],
        description="手机",
        render_kw={
            "class": "form-control",
            "placeholder": "手机"
        }
    )
    avatar = FileField(
        label="<span class='glyphicon glyphicon-picture'></span>头像",
        validators=[
            FileRequired("请上传头像！")
        ],
        description="头像",
    )
    info = TextAreaField(
        label="<span class='glyphicon glyphicon-edit'></span>简介",
        validators=[
            DataRequired("请输入简介！")
        ],
        description="简介",
        render_kw={
            "class": "form-control",
            "rows": 10,
            "placeholder": "爱电影，爱生活"
        }
    )
    submit = SubmitField(
        '保存修改',
        render_kw={
            "class": "btn btn-success"
        }
    )


class PwdForm(FlaskForm):
    """
    密码表单
    """
    old_pwd = PasswordField(
        label="<span class='glyphicon glyphicon-lock'></span>旧密码",
        validators=[
            DataRequired("请输入旧密码！")
        ],
        description="旧密码",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入旧密码！",
            "autofocus": "autofocus"
        }
    )
    new_pwd = PasswordField(
        label="<span class='glyphicon glyphicon-lock'></span>新密码",
        validators=[
            DataRequired("请输入新密码！")
        ],
        description="新密码",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入新密码！"
        }
    )
    submit = SubmitField(
        '修改密码',
        render_kw={
            "class": "btn btn-success"
        }
    )

    def validate_old_pwd(self, filed):
        from flask import session
        pwd = filed.data
        name = session["user"]
        user = User.query.filter_by(name=name).first()
        if not user.check_pwd(pwd):
            raise ValidationError("旧密码错误！")


class CommentForm(FlaskForm):
    """
    评论表单
    """
    content = TextAreaField(
        label="内容",
        description="内容",
        render_kw={
            "id": "input_content"
        }
    )
    submit = SubmitField(
        '提交评论',
        render_kw={
            "class": "btn btn-success",
            "id": "btn-sub"
        }
    )

    def validate_content(self, filed):
        content = filed.data
        if not content:
            raise ValidationError("评论不能为空！")
