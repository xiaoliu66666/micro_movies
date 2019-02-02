import stat

from . import admin
from flask import render_template, redirect, url_for, flash, session, request
from app.admin.forms import LoginForm, TagForm, MovieForm, PreViewForm, PwdForm, AuthForm, RoleForm, AdminForm
from app.models import Admin, Tag, Movie, Preview, User, Comment, MovieCol, OpLog, AdminLog, UserLog, Auth, Role
from functools import wraps
from app import db, app
from werkzeug.utils import secure_filename
import os
import uuid
import datetime


# 上下文处理器
@admin.context_processor
def tpt_extra():
    data = dict(
        online_datetime=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    return data


# 登录控制
def admin_login_req(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        if "admin" not in session:
            return redirect(url_for("admin.login", next=request.url))
        return f(*args, **kwargs)

    return decorator


# 权限控制
def admin_auth(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        admin = Admin.query.join(
            Role
        ).filter(
            Role.id == Admin.role_id,
            Admin.id == session["admin_id"]
        ).first()
        auths = admin.role.auths
        auths = list(int(i) for i in auths.split(","))
        auth_list = Auth.query.all()
        rules = [v.url for v in auth_list for val in auths if v.id == val]
        rules.append("/admin/")
        rule = request.url_rule

        if str(rule) not in rules:
            return render_template("admin/no_auth.html")
        return f(*args, **kwargs)

    return decorator


# 修改文件名称
def change_filename(filename):
    file_info = os.path.splitext(filename)
    filename = datetime.datetime.now().strftime("%Y%m%d%H%M%S") + str(uuid.uuid4().hex) + file_info[1]
    return filename


# 首页
@admin.route("/")
@admin_login_req
@admin_auth
def index():
    return render_template("admin/index.html")


# 登录
@admin.route("/login/", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        data = form.data
        admin = Admin.query.filter_by(name=data["account"]).first()
        if not admin.check_pwd(data["pwd"]):
            flash("密码错误！", "err")
            return redirect(url_for('admin.login'))
        session["admin"] = data["account"]
        session["admin_id"] = admin.id
        adminlog = AdminLog(
            admin_id=admin.id,
            ip=request.remote_addr
        )
        db.session.add(adminlog)
        db.session.commit()
        return redirect(request.args.get("next") or url_for('admin.index'))
    return render_template("admin/login.html", form=form)


# 登出
@admin.route("/logout/")
@admin_login_req
def logout():
    session.pop("admin", None)
    session.pop("admin_id", None)
    return redirect(url_for("admin.login"))


# 修改密码
@admin.route("/pwd/", methods=["GET", "POST"])
@admin_login_req
def pwd():
    form = PwdForm()
    if form.validate_on_submit():
        data = form.data
        admin = Admin.query.filter_by(name=session["admin"]).first()
        from werkzeug.security import generate_password_hash
        admin.pwd = generate_password_hash(data["new_pwd"])
        db.session.add(admin)
        db.session.commit()
        flash("修改密码成功，请重新登录！", "ok")
        return redirect(url_for("admin.logout"))
    return render_template("admin/pwd.html", form=form)


# 添加标签
@admin.route("/tag/add/", methods=["GET", "POST"])
@admin_login_req
@admin_auth
def tag_add():
    form = TagForm()
    if form.validate_on_submit():
        data = form.data
        tag = Tag.query.filter_by(name=data["name"]).count()

        if tag == 1:
            flash("此标签已经存在，请勿重复添加!", "err")
            return redirect(url_for("admin.tag_add"))
        tag = Tag(
            name=data["name"]
        )
        db.session.add(tag)
        db.session.commit()
        flash("添加标签成功！", "ok")
        oplog = OpLog(
            admin_id=session["admin_id"],
            # remote_addr是一个属性方法
            ip=request.remote_addr,
            reason="添加标签：{}".format(data["name"])
        )
        db.session.add(oplog)
        db.session.commit()
        return redirect(url_for("admin.tag_add"))
    return render_template("admin/tag_add.html", form=form)


# 编辑标签
@admin.route("/tag/edit/<int:t_id>/", methods=["GET", "POST"])
@admin_login_req
@admin_auth
def tag_edit(t_id=None):
    form = TagForm()
    tag = Tag.query.get_or_404(int(t_id))
    if form.validate_on_submit():
        data = form.data
        tag_cnt = Tag.query.filter_by(name=data["name"]).count()

        if tag.name != data["name"] and tag_cnt == 1:
            flash("此标签已经存在，请勿重复添加!", "err")
            return redirect(url_for("admin.tag_edit", t_id=t_id))

        tag.name = data["name"]
        db.session.add(tag)
        db.session.commit()
        flash("修改标签成功！", "ok")
        return redirect(url_for("admin.tag_edit", t_id=t_id))
    return render_template("admin/tag_edit.html", form=form, tag=tag)


# 标签列表
@admin.route("/tag/list/<int:page>/")
@admin_login_req
@admin_auth
def tag_list(page=1):
    page_data = Tag.query.order_by(Tag.id).paginate(page=page, per_page=10)
    return render_template("admin/tag_list.html", page_data=page_data)


# 删除标签
@admin.route("/tag/del/<int:t_id>/")
@admin_login_req
@admin_auth
def tag_del(t_id=None):
    tag = Tag.query.filter_by(id=t_id).first_or_404()
    db.session.delete(tag)
    db.session.commit()
    flash("删除标签成功！", "ok")
    return redirect(url_for("admin.tag_list", page=1))


# 添加电影
@admin.route("/movie/add/", methods=["GET", "POST"])
@admin_login_req
def movie_add():
    form = MovieForm()
    if form.validate_on_submit():
        data = form.data
        url_filename = secure_filename(form.url.data.filename)
        cover_filename = secure_filename(form.cover.data.filename)

        if not os.path.exists(app.config["UP_DIR"]):
            # 创建一个多级目录
            os.makedirs(app.config["UP_DIR"])
            os.chmod(app.config["UP_DIR"], stat.S_IRWXU)

        url = change_filename(url_filename)
        cover = change_filename(cover_filename)
        form.url.data.save(app.config["UP_DIR"] + url)
        form.cover.data.save(app.config["UP_DIR"] + cover)
        movie = Movie(
            title=data["title"],
            url=url,
            info=data["info"],
            cover=cover,
            star=int(data["star"]),
            play_num=0,
            comment_num=0,
            tag_id=int(data["tag_id"]),
            area=data["area"],
            release_time=data["release_time"],
            length=data["length"]
        )
        db.session.add(movie)
        db.session.commit()
        flash("添加电影成功！", "ok")
        return redirect(url_for("admin.movie_add"))
    return render_template("admin/movie_add.html", form=form)


# 电影列表
@admin.route("/movie/list/<int:page>/")
@admin_login_req
def movie_list(page=1):
    page_data = Movie.query.join(Tag).filter(
        Tag.id == Movie.tag_id
    ).order_by(Movie.id).paginate(page=page, per_page=10)
    return render_template("admin/movie_list.html", page_data=page_data)


# 删除电影
@admin.route("/movie/del/<int:m_id>/")
@admin_login_req
def movie_del(m_id=None):
    movie = Movie.query.filter_by(id=m_id).first_or_404()
    db.session.delete(movie)
    db.session.commit()
    os.remove(app.config["UP_DIR"] + movie.url)
    os.remove(app.config["UP_DIR"] + movie.cover)
    flash("删除电影成功！", "ok")
    return redirect(url_for("admin.movie_list", page=1))


# 编辑电影
@admin.route("/movie/edit/<int:m_id>/", methods=["GET", "POST"])
@admin_login_req
def movie_edit(m_id=None):
    form = MovieForm()
    form.url.validators = []
    form.cover.validators = []
    movie = Movie.query.get_or_404(int(m_id))

    if request.method == "GET":
        form.info.data = movie.info
        form.star.data = movie.star
        form.tag_id.data = movie.tag_id

    if form.validate_on_submit():
        data = form.data

        if not os.path.exists(app.config["UP_DIR"]):
            # 创建一个多级目录
            os.makedirs(app.config["UP_DIR"])
            os.chmod(app.config["UP_DIR"], stat.S_IRWXU)

        if form.url.data.filename != "":
            url_filename = secure_filename(form.url.data.filename)
            movie.url = change_filename(url_filename)
            form.url.data.save(app.config["UP_DIR"] + movie.url)

        if form.cover.data.filename != "":
            cover_filename = secure_filename(form.cover.data.filename)
            movie.cover = change_filename(cover_filename)
            form.cover.data.save(app.config["UP_DIR"] + movie.cover)

        movie.title = data["title"]
        movie.info = data["info"]
        movie.star = data["star"]
        movie.tag_id = data["tag_id"]
        movie.area = data["area"]
        movie.length = data["length"]
        movie.release_time = data["release_time"]
        db.session.add(movie)
        db.session.commit()
        flash("添加电影成功！", "ok")
        return redirect(url_for("admin.movie_edit", m_id=m_id))
    return render_template("admin/movie_edit.html", form=form, movie=movie)


# 添加预告
@admin.route("/preview/add/", methods=["GET", "POST"])
@admin_login_req
def preview_add():
    form = PreViewForm()
    if form.validate_on_submit():
        data = form.data
        cover_filename = secure_filename(form.cover.data.filename)

        if not os.path.exists(app.config["UP_DIR"]):
            # 创建一个多级目录
            os.makedirs(app.config["UP_DIR"])
            os.chmod(app.config["UP_DIR"], stat.S_IRWXU)

        cover = change_filename(cover_filename)
        form.cover.data.save(app.config["UP_DIR"] + cover)
        preview = Preview(
            title=data["title"],
            cover=cover
        )
        db.session.add(preview)
        db.session.commit()
        flash("添加预告成功！", "ok")
        return redirect(url_for('admin.preview_add'))
    return render_template("admin/preview_add.html", form=form)


# 预告列表
@admin.route("/preview/list/<int:page>")
@admin_login_req
def preview_list(page=1):
    page_data = Preview.query.order_by(Preview.id).paginate(page=page, per_page=10)
    return render_template("admin/preview_list.html", page_data=page_data)


# 删除预告
@admin.route("/preview/del/<int:p_id>/")
@admin_login_req
def preview_del(p_id=None):
    preview = Preview.query.filter_by(id=p_id).first_or_404()
    db.session.delete(preview)
    db.session.commit()
    os.remove(app.config["UP_DIR"] + preview.cover)
    flash("删除预告成功！", "ok")
    return redirect(url_for("admin.movie_list", page=1))


# 编辑预告
@admin.route("/preview/edit/<int:p_id>/", methods=["GET", "POST"])
@admin_login_req
def preview_edit(p_id=None):
    form = PreViewForm()
    form.cover.validators = []
    preview = Preview.query.get_or_404(int(p_id))
    if request.method == "GET":
        form.title.data = preview.title
    if form.validate_on_submit():
        data = form.data

        if form.cover.data.filename != "":
            cover_filename = secure_filename(form.cover.data.filename)
            preview.cover = change_filename(cover_filename)
            form.cover.data.save(app.config["UP_DIR"] + preview.cover)

        preview.title = data["title"]
        db.session.add(preview)
        db.session.commit()
        flash("修改预告成功！", "ok")
        return redirect(url_for('admin.preview_edit', p_id=p_id))
    return render_template("admin/preview_edit.html", form=form, preview=preview)


# 会员列表
@admin.route("/user/list/<int:page>/")
@admin_login_req
def user_list(page=1):
    page_data = User.query.order_by(User.addtime.desc()).paginate(page=page, per_page=10)
    return render_template("admin/user_list.html", page_data=page_data)


# 会员详情
@admin.route("/user/view/<int:u_id>/")
@admin_login_req
def user_view(u_id=None):
    user = User.query.get_or_404(int(u_id))
    return render_template("admin/user_view.html", user=user)


# 删除会员
@admin.route("/user/del/<int:u_id>/")
@admin_login_req
def user_del(u_id=None):
    user = User.query.get_or_404(int(u_id))
    db.session.delete(user)
    db.session.commit()
    flash("删除会员成功！", "ok")
    return redirect(url_for("admin.user_list", page=1))


# 评论列表
@admin.route("/comment/list/<int:page>/")
@admin_login_req
def comment_list(page=1):
    page_data = Comment.query.join(
        Movie
    ).join(
        User
    ).filter(
        User.id == Comment.user_id,
        Movie.id == Comment.movie_id
    ).order_by(
        Comment.addtime.desc()
    ).paginate(page=page, per_page=10)
    return render_template("admin/comment_list.html", page_data=page_data)


# 删除评论
@admin.route("/comment/del/<int:c_id>/")
@admin_login_req
def comment_del(c_id=None):
    comment = Comment.query.get_or_404(int(c_id))
    db.session.delete(comment)
    db.session.commit()
    flash("删除评论成功！", "ok")
    return redirect(url_for("admin.comment_list", page=1))


# 收藏列表
@admin.route("/moviecol/list/<int:page>/")
@admin_login_req
def moviecol_list(page=1):
    page_data = MovieCol.query.join(
        Movie
    ).join(
        User
    ).filter(
        User.id == MovieCol.user_id,
        Movie.id == MovieCol.movie_id
    ).order_by(
        MovieCol.addtime.desc()
    ).paginate(page=page, per_page=10)
    return render_template("admin/moviecol_list.html", page_data=page_data)


# 删除收藏
@admin.route("/moviecol/del/<int:m_id>/")
@admin_login_req
def moviecol_del(m_id=None):
    moviecol = MovieCol.query.get_or_404(int(m_id))
    db.session.delete(moviecol)
    db.session.commit()
    flash("删除收藏成功！", "ok")
    return redirect(url_for("admin.moviecol_list", page=1))


# 操作日志
@admin.route("/oplog/list/<int:page>/")
@admin_login_req
def oplog_list(page=1):
    page_data = OpLog.query.join(
        Admin
    ).filter(
        Admin.id == OpLog.admin_id
    ).order_by(
        OpLog.addtime.desc()
    ).paginate(page=page, per_page=10)
    return render_template("admin/oplog_list.html", page_data=page_data)


# 管理员登录日志
@admin.route("/adminloginlog/list/<int:page>/")
@admin_login_req
def adminloginlog_list(page=1):
    page_data = AdminLog.query.join(
        Admin
    ).filter(
        Admin.id == AdminLog.admin_id
    ).order_by(
        AdminLog.addtime.desc()
    ).paginate(page=page, per_page=10)
    return render_template("admin/adminloginlog_list.html", page_data=page_data)


# 用户登录日志
@admin.route("/userloginlog/list/<int:page>/")
@admin_login_req
def userloginlog_list(page=1):
    page_data = UserLog.query.join(
        User
    ).filter(
        User.id == UserLog.user_id
    ).order_by(
        UserLog.addtime.desc()
    ).paginate(page=page, per_page=10)
    return render_template("admin/userloginlog_list.html", page_data=page_data)


# 添加角色
@admin.route("/role/add/", methods=["GET", "POST"])
@admin_login_req
def role_add():
    form = RoleForm()
    if form.validate_on_submit():
        data = form.data
        role = Role(
            name=data["name"],
            auths=",".join(str(i) for i in data["auths"])
        )
        db.session.add(role)
        db.session.commit()
        flash("添加角色成功！", "ok")
    return render_template("admin/role_add.html", form=form)


# 角色列表
@admin.route("/role/list/<int:page>/")
@admin_login_req
def role_list(page=1):
    page_data = Role.query.order_by(
        Role.addtime.desc()
    ).paginate(page=page, per_page=10)
    return render_template("admin/role_list.html", page_data=page_data)


# 删除角色
@admin.route("/role/del/<int:r_id>/")
@admin_login_req
def role_del(r_id=None):
    role = Role.query.get_or_404(int(r_id))
    db.session.delete(role)
    db.session.commit()
    flash("删除角色成功！", "ok")
    return redirect(url_for("admin.role_list", page=1))


# 编辑角色
@admin.route("/role/edit/<int:r_id>/", methods=["GET", "POST"])
@admin_login_req
def role_edit(r_id=None):
    form = RoleForm()
    role = Role.query.get_or_404(int(r_id))

    if request.method == "GET":
        form.auths.data = list(int(i) for i in role.auths.split(","))

    if form.validate_on_submit():
        data = form.data
        role.name = data["name"]
        role.auths = ",".join(str(i) for i in data["auths"])
        db.session.add(role)
        db.session.commit()
        flash("修改角色成功！", "ok")
        return redirect(url_for("admin.role_edit", r_id=r_id))
    return render_template("admin/role_edit.html", form=form, role=role)


# 添加权限
@admin.route("/auth/add/", methods=["GET", "POST"])
@admin_login_req
def auth_add():
    form = AuthForm()
    if form.validate_on_submit():
        data = form.data
        auth = Auth(
            name=data["name"],
            url=data["url"]
        )
        db.session.add(auth)
        db.session.commit()
        flash("添加权限成功！", "ok")
    return render_template("admin/auth_add.html", form=form)


# 权限列表
@admin.route("/auth/list/<int:page>/")
@admin_login_req
def auth_list(page=1):
    page_data = Auth.query.order_by(
        Auth.addtime.desc()
    ).paginate(page=page, per_page=10)
    return render_template("admin/auth_list.html", page_data=page_data)


# 删除权限
@admin.route("/auth/del/<int:a_id>/")
@admin_login_req
def auth_del(a_id=None):
    auth = Auth.query.filter_by(id=a_id).first_or_404()
    db.session.delete(auth)
    db.session.commit()
    flash("删除权限成功！", "ok")
    return redirect(url_for("admin.auth_list", page=1))


# 编辑权限
@admin.route("/auth/edit/<int:a_id>/", methods=["GET", "POST"])
@admin_login_req
def auth_edit(a_id=None):
    form = AuthForm()
    auth = Auth.query.get_or_404(int(a_id))
    if form.validate_on_submit():
        data = form.data
        auth.url = data["url"]
        auth.name = data["name"]
        db.session.add(auth)
        db.session.commit()
        flash("修改权限成功！", "ok")
        return redirect(url_for("admin.auth_edit", a_id=a_id))
    return render_template("admin/auth_edit.html", form=form, auth=auth)


# 添加管理员
@admin.route("/admin/add/", methods=["GET", "POST"])
@admin_login_req
def admin_add():
    form = AdminForm()
    if form.validate_on_submit():
        from werkzeug.security import generate_password_hash
        data = form.data
        admin = Admin(
            name=data["name"],
            pwd=generate_password_hash(data["pwd"]),
            role_id=data["role_id"],
            is_super=0
        )
        db.session.add(admin)
        db.session.commit()
        flash("添加管理员成功！", "ok")
    return render_template("admin/admin_add.html", form=form)


# 管理员列表
@admin.route("/admin/list/<int:page>/")
@admin_login_req
def admin_list(page=1):
    page_data = Admin.query.join(
        Role
    ).filter(
        Role.id == Admin.role_id
    ).order_by(
        Admin.addtime.desc()
    ).paginate(page=page, per_page=10)
    return render_template("admin/admin_list.html", page_data=page_data)
