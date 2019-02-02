import datetime
import json
import os
import stat
from functools import wraps

from werkzeug.utils import secure_filename

from . import home
from flask import render_template, redirect, url_for, flash, session, request
from app.home.forms import RegisterForm, LoginForm, UserForm, PwdForm, CommentForm
from werkzeug.security import generate_password_hash
from app import db, app
from app.models import User, UserLog, Preview, Tag, Movie, Comment, MovieCol
import uuid


# 登录控制
def user_login_req(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        if "user" not in session:
            flash("请登录后再尝试！", "err")
            return redirect(url_for("home.login", next=request.url))
        return f(*args, **kwargs)

    return decorator


# 修改文件名称
def change_filename(filename):
    file_info = os.path.splitext(filename)
    filename = datetime.datetime.now().strftime("%Y%m%d%H%M%S") + str(uuid.uuid4().hex) + file_info[1]
    return filename


@home.route("/login/", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        data = form.data
        u = User.query.filter_by(name=data["name"]).first()
        if not u:
            flash("账户不存在！", "err")
            return redirect(url_for('home.login'))
        if not u.check_pwd(data["pwd"]):
            flash("密码错误！", "err")
            return redirect(url_for('home.login'))
        session["user"] = u.name
        session["user_id"] = u.id
        user_log = UserLog(
            user_id=u.id,
            ip=request.remote_addr
        )
        db.session.add(user_log)
        db.session.commit()

        next_w = request.args.get("next")
        if not next_w or not next_w.startswith('/'):
            next_w = url_for('home.index', page=1)
        return redirect(next_w)

    return render_template("home/login.html", form=form)


@home.route("/logout/")
def logout():
    session.pop("user", None)
    session.pop("user_id", None)
    return redirect(url_for("home.login"))


@home.route("/register/", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        data = form.data
        new_user = User(
            name=data["name"],
            email=data["email"],
            phone=data["phone"],
            pwd=generate_password_hash(data["pwd"]),
            uuid=uuid.uuid4().hex
        )
        db.session.add(new_user)
        db.session.commit()
        flash("注册成功！", "ok")
    return render_template("home/register.html", form=form)


@home.route("/user/", methods=["GET", "POST"])
@user_login_req
def user():
    form = UserForm()
    c_user = User.query.get(session["user_id"])
    form.avatar.validators = []
    if request.method == "GET":
        form.name.data = c_user.name
        form.email.data = c_user.email
        form.phone.data = c_user.phone
        form.info.data = c_user.info
    if form.validate_on_submit():
        data = form.data
        avatar_filename = secure_filename(form.avatar.data.filename)

        if not os.path.exists(app.config["USER_DIR"]):
            os.makedirs(app.config["USER_DIR"])
            os.chmod(app.config["USER_DIR"], stat.S_IRWXU)

        avatar = change_filename(avatar_filename)
        form.avatar.data.save(app.config["USER_DIR"] + avatar)

        name_cnt = User.query.filter_by(name=data["name"]).count()
        if name_cnt == 1 and data["name"] != c_user.name:
            flash("昵称已存在！", "err")
            return redirect(url_for('home.user'))

        email_cnt = User.query.filter_by(email=data["email"]).count()
        if email_cnt == 1 and data["email"] != c_user.email:
            flash("邮箱已存在！", "err")
            return redirect(url_for('home.user'))

        phone_cnt = User.query.filter_by(phone=data["phone"]).count()
        if phone_cnt == 1 and data["phone"] != c_user.phone:
            flash("手机已存在！", "err")
            return redirect(url_for('home.user'))

        c_user.name = data["name"],
        c_user.email = data["email"],
        c_user.phone = data["phone"],
        c_user.info = data["info"],
        c_user.avatar = avatar

        db.session.add(c_user)
        db.session.commit()
        flash("修改成功！", "ok")
        return redirect(url_for('home.user'))
    return render_template("home/user.html", form=form, user=c_user)


@home.route("/pwd/", methods=["GET", "POST"])
@user_login_req
def pwd():
    form = PwdForm()
    if form.validate_on_submit():
        data = form.data
        c_user = User.query.filter_by(name=session["user"]).first()
        user.pwd = generate_password_hash(data["new_pwd"])
        db.session.add(c_user)
        db.session.commit()
        flash("修改密码成功，请重新登录！", "ok")
        return redirect(url_for("home.logout"))
    return render_template("home/pwd.html", form=form)


# 评论记录
@home.route("/comments/<int:page>/")
@user_login_req
def comments(page=1):
    page_data = Comment.query.join(
        Movie
    ).join(
        User
    ).filter(
        User.id == session["user_id"],
        Movie.id == Comment.movie_id
    ).order_by(
        Comment.addtime.desc()
    ).paginate(page=page, per_page=10)
    return render_template("home/comments.html", page_data=page_data)


# 登录日志
@home.route("/loginlog/<int:page>/")
@user_login_req
def loginlog(page=1):
    page_data = UserLog.query.filter_by(
        user_id=int(session["user_id"])
    ).order_by(
        UserLog.addtime.desc()
    ).paginate(page=page, per_page=10)
    return render_template("home/loginlog.html", page_data=page_data)


# 添加收藏
@home.route("/moviecol/add/")
@user_login_req
def moviecol_add():
    mid = request.args.get("mid", "")
    uid = request.args.get("uid", "")
    movie_col = MovieCol.query.filter_by(
        movie_id=int(mid),
        user_id=int(uid)
    ).count()
    if movie_col == 1:
        data = dict(ok=0)
    if movie_col == 0:
        movie_col = MovieCol(
            movie_id=int(mid),
            user_id=int(uid)
        )
        db.session.add(movie_col)
        db.session.commit()
        data = dict(ok=1)
    return json.dumps(data)


# 电影收藏
@home.route("/moviecol/<int:page>/")
@user_login_req
def moviecol(page=1):
    page_data = MovieCol.query.join(
        Movie
    ).join(
        User
    ).filter(
        User.id == int(session["user_id"]),
        Movie.id == MovieCol.movie_id
    ).order_by(
        MovieCol.addtime.desc()
    ).paginate(page=page, per_page=10)
    return render_template("home/moviecol.html", page_data=page_data)


# 首页
@home.route("/<int:page>/")
def index(page=1):
    tags = Tag.query.all()
    movie = Movie.query

    tid = request.args.get("tid", 0)
    if int(tid) != 0:
        movie = movie.filter_by(tag_id=int(tid))

    star = request.args.get("star", 0)
    if int(star) != 0:
        movie = movie.filter_by(star=int(star))

    time = request.args.get("time", 0)
    if int(time) != 0:
        if int(time) == 1:
            movie = movie.order_by(Movie.addtime.desc())
        else:
            movie = movie.order_by(Movie.addtime.asc())

    pm = request.args.get("pm", 0)
    if int(pm) != 0:
        if int(pm) == 1:
            movie = movie.order_by(Movie.play_num.desc())
        else:
            movie = movie.order_by(Movie.play_num.asc())

    cm = request.args.get("cm", 0)
    if int(cm) != 0:
        if int(cm) == 1:
            movie = movie.order_by(Movie.comment_num.desc())
        else:
            movie = movie.order_by(Movie.comment_num.asc())

    page_data = movie.paginate(page=page, per_page=10)
    p = {
        "tid": tid,
        "star": star,
        "time": time,
        "pm": pm,
        "cm": cm
    }

    return render_template("home/index.html", tags=tags, p=p, page_data=page_data)


# 上映预告
@home.route("/animation/")
def animation():
    data = Preview.query.all()
    return render_template("home/animation.html", data=data)


# 搜索电影
@home.route("/search/<int:page>/")
def search(page=1):
    key = request.args.get("key", "")

    movie_cnt = Movie.query.filter(
        Movie.title.like("%" + key + "%")
    ).count()

    page_data = Movie.query.filter(
        Movie.title.like("%" + key + "%")
    ).order_by(
        Movie.addtime.desc()
    ).paginate(page=page, per_page=10)
    page_data.key = key
    return render_template("home/search.html", key=key, page_data=page_data, movie_cnt=movie_cnt)


@home.route("/play/<int:id>/<int:page>/", methods=["GET", "POST"])
def play(id=None, page=1):
    movie = Movie.query.join(
        Tag
    ).filter(
        Tag.id == Movie.tag_id,
        Movie.id == int(id)
    ).first_or_404()
    movie.play_num += 1

    page_data = Comment.query.join(
        Movie
    ).join(
        User
    ).filter(
        User.id == Comment.user_id,
        Movie.id == movie.id
    ).order_by(
        Comment.addtime.desc()
    ).paginate(page=page, per_page=10)

    form = CommentForm()
    if "user" in session and form.validate_on_submit():
        data = form.data
        comment = Comment(
            content=data["content"],
            movie_id=movie.id,
            user_id=session["user_id"]
        )
        movie.comment_num += 1
        db.session.add(comment)
        db.session.commit()
        flash("添加评论成功！", "ok")
        return redirect(url_for('home.play', id=movie.id, page=1))

    db.session.add(movie)
    db.session.commit()
    return render_template("home/play.html", movie=movie, form=form, page_data=page_data)
