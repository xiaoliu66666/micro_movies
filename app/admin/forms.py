from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired
from wtforms import StringField, SubmitField, PasswordField, FileField, TextAreaField, SelectField, SelectMultipleField
from wtforms.validators import DataRequired, ValidationError, EqualTo
from app.models import Admin, Tag, Movie, Preview, Auth, Role

tag_list = Tag.query.all()
auth_list = Auth.query.all()
role_list = Role.query.all()


class LoginForm(FlaskForm):
    """
    登录表单
    """
    account = StringField(
        label="账号",
        validators=[
            DataRequired("请输入账号！")
        ],
        description="账号",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入账号！",
            "autofocus": "autofocus",
            "required": "required"
        }
    )
    pwd = PasswordField(
        label="密码",
        validators=[
            DataRequired("请输入密码！")
        ],
        description="密码",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入密码！",
            "required": "required"
        }
    )
    submit = SubmitField(
        '登录',
        render_kw={
            "class": "btn btn-primary btn-block btn-flat",
        }
    )

    def validate_account(self, filed):
        account = filed.data
        admin = Admin.query.filter_by(name=account).count()
        if admin == 0:
            raise ValidationError("账号不存在！")


class TagForm(FlaskForm):
    """
    标签表单
    """
    name = StringField(
        label="标签",
        validators=[
            DataRequired("请输入标签！")
        ],
        description="标签",
        render_kw={
            "autofocus": "autofocus",
            "class": "form-control",
            "id": "input_name",
            "placeholder": "请输入标签名称！"
        }
    )
    submit = SubmitField(
        '确定',
        render_kw={
            "class": "btn btn-primary"
        }
    )


class MovieForm(FlaskForm):
    """
    电影表单
    """
    title = StringField(
        label="片名",
        validators=[
            DataRequired("请输入片名！")
        ],
        description="片名",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入片名！"
        }
    )
    url = FileField(
        label="文件",
        validators=[
            FileRequired("请上传文件！")
        ],
        description="文件",
    )
    info = TextAreaField(
        label="简介",
        validators=[
            DataRequired("请输入简介！")
        ],
        description="简介",
        render_kw={
            "class": "form-control",
            "rows": 10
        }
    )
    cover = FileField(
        label="封面",
        validators=[
            FileRequired("请上传封面！")
        ],
        description="封面",
    )
    star = SelectField(
        label="星级",
        validators=[
            DataRequired("请选择星级！")
        ],
        coerce=int,
        choices=[(1, "1星"), (2, "2星"), (3, "3星"), (4, "4星"), (5, "5星")],
        description="星级",
        render_kw={
            "class": "form-control"
        }
    )
    tag_id = SelectField(
        label="标签",
        validators=[
            DataRequired("请选择标签！")
        ],
        coerce=int,
        choices=[(v.id, v.name) for v in tag_list],
        description="标签",
        render_kw={
            "class": "form-control"
        }
    )
    area = StringField(
        label="上映地区",
        validators=[
            DataRequired("请输入片名！")
        ],
        description="上映地区",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入上映地区！"
        }
    )
    length = StringField(
        label="片长",
        validators=[
            DataRequired("请输入片长！")
        ],
        description="片长",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入片长！"
        }
    )
    release_time = StringField(
        label="上映时间",
        validators=[
            DataRequired("请输入上映时间！")
        ],
        description="上映时间",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入上映时间！",
            "id": "input_release_time"
        }
    )
    submit = SubmitField(
        '确定',
        render_kw={
            "class": "btn btn-primary"
        }
    )

    def validate_title(self, filed):
        title = filed.data
        movie_cnt = Movie.query.filter_by(title=title).count()
        if movie_cnt == 1:
            raise ValidationError("电影已存在，请不要重复添加！")


class PreViewForm(FlaskForm):
    """
    预告表单
    """
    title = StringField(
        label="预告标题",
        validators=[
            DataRequired("请输入预告标题！")
        ],
        description="预告标题",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入预告标题！"
        }
    )

    cover = FileField(
        label="预告封面",
        validators=[
            FileRequired("请上传封面！")
        ],
        description="预告封面",
    )

    submit = SubmitField(
        '确定',
        render_kw={
            "class": "btn btn-primary"
        }
    )


class PwdForm(FlaskForm):
    """
    密码表单
    """
    old_pwd = PasswordField(
        label="旧密码",
        validators=[
            DataRequired("请输入旧密码！")
        ],
        description="旧密码",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入旧密码！",
            "autofocus": "autofocus",
            "required": "required"
        }
    )
    new_pwd = PasswordField(
        label="新密码",
        validators=[
            DataRequired("请输入新密码！")
        ],
        description="新密码",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入新密码！",
            "required": "required"
        }
    )
    submit = SubmitField(
        '确定',
        render_kw={
            "class": "btn btn-primary"
        }
    )

    def validate_old_pwd(self, filed):
        from flask import session
        pwd = filed.data
        name = session["admin"]
        admin = Admin.query.filter_by(name=name).first()
        if not admin.check_pwd(pwd):
            raise ValidationError("旧密码错误！")


class AuthForm(FlaskForm):
    """
    权限表单
    """
    name = StringField(
        label="权限名称",
        validators=[
            DataRequired("请输入权限名称！")
        ],
        description="权限名称",
        render_kw={
            "autofocus": "autofocus",
            "class": "form-control",
            "placeholder": "请输入权限名称！"
        }
    )
    url = StringField(
        label="权限地址",
        validators=[
            DataRequired("请输入权限地址称！")
        ],
        description="权限地址",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入权限地址！"
        }
    )
    submit = SubmitField(
        '确定',
        render_kw={
            "class": "btn btn-primary"
        }
    )


class RoleForm(FlaskForm):
    """
    角色表单
    """
    name = StringField(
        label="角色名称",
        validators=[
            DataRequired("请输入角色名称！")
        ],
        description="角色名称",
        render_kw={
            "autofocus": "autofocus",
            "class": "form-control",
            "placeholder": "请输入角色名称！"
        }
    )
    auths = SelectMultipleField(
        label="权限列表",
        validators=[
            DataRequired("请选择权限！")
        ],
        coerce=int,
        choices=[(v.id, v.name) for v in auth_list],
        description="权限列表",
        render_kw={
            "class": "form-control"
        }
    )
    submit = SubmitField(
        '确定',
        render_kw={
            "class": "btn btn-primary"
        }
    )


class AdminForm(FlaskForm):
    """
    管理员表单
    """
    name = StringField(
        label="管理员账号",
        validators=[
            DataRequired("请输入管理员账号！")
        ],
        description="管理员账号",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入管理员账号！",
            "autofocus": "autofocus"
        }
    )
    pwd = PasswordField(
        label="管理员密码",
        validators=[
            DataRequired("请输入管理员密码！")
        ],
        description="管理员密码",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入管理员密码！"
        }
    )
    pwd2 = PasswordField(
        label="重复管理员密码",
        validators=[
            DataRequired("请再次输入管理员密码！"),
            EqualTo("pwd", "两次密码不一致！")
        ],
        description="重复管理员密码",
        render_kw={
            "class": "form-control",
            "placeholder": "请再次输入管理员密码！"
        }
    )
    role_id = SelectField(
        label="所属角色",
        validators=[
            DataRequired("请选择所属角色！")
        ],
        coerce=int,
        choices=[(v.id, v.name) for v in role_list],
        description="所属角色",
        render_kw={
            "class": "form-control"
        }
    )
    submit = SubmitField(
        '确认',
        render_kw={
            "class": "btn btn-primary",
        }
    )