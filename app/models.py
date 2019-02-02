from datetime import datetime

from app import db


# 会员
class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)  # 编号
    name = db.Column(db.String(100), unique=True)  # 昵称
    pwd = db.Column(db.String(100))  # 密码
    email = db.Column(db.String(100), unique=True)  # 邮箱
    phone = db.Column(db.String(11), unique=True)  # 手机号
    info = db.Column(db.Text)  # 个人简介
    avatar = db.Column(db.String(255), unique=True)  # 头像
    addtime = db.Column(db.DateTime, index=True,
                        default=datetime.now)  # 注册时间
    uuid = db.Column(db.String(255), unique=True)  # 唯一标志符
    # 会员日志关系关联
    user_logs = db.relationship("UserLog", backref="user")  # 会员日志外键关系关联
    comments = db.relationship("Comment", backref="user")  # 评论外键关系关联
    movie_cols = db.relationship("MovieCol", backref="user")  # 收藏外键关系关联

    def __repr__(self):
        return "<User {}>".format(self.name)

    def check_pwd(self, pwd):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.pwd, pwd)


# 会员登录日志
class UserLog(db.Model):
    __tablename__ = "userLog"
    id = db.Column(db.Integer, primary_key=True)  # 编号
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))  # 所属会员
    ip = db.Column(db.String(100))  # 登录IP
    addtime = db.Column(db.DateTime, index=True,
                        default=datetime.now)  # 登录时间

    def __repr__(self):
        return "<UserLog {}>".format(self.id)


# 标签
class Tag(db.Model):
    __tablename__ = "tag"
    id = db.Column(db.Integer, primary_key=True)  # 编号
    name = db.Column(db.String(100), unique=True)  # 标签名
    addtime = db.Column(db.DateTime, index=True,
                        default=datetime.now)  # 添加时间
    movies = db.relationship("Movie", backref="tag")  # 电影外键关系关联

    def __repr__(self):
        return "<Tag {}>".format(self.name)


# 电影
class Movie(db.Model):
    __tablename__ = "movie"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))  # 片名
    url = db.Column(db.String(255), unique=True)  # 播放地址
    info = db.Column(db.Text)  # 简介
    cover = db.Column(db.String(255), unique=True)  # 封面
    star = db.Column(db.SmallInteger)  # 星级
    play_num = db.Column(db.BigInteger)  # 播放量
    comment_num = db.Column(db.BigInteger)  # 评论量
    tag_id = db.Column(db.Integer, db.ForeignKey("tag.id"))  # 所属标签
    area = db.Column(db.String(255))  # 上映地区
    release_time = db.Column(db.Date)  # 上映时间
    length = db.Column(db.String(100))  # 片长
    addtime = db.Column(db.DateTime, index=True,
                        default=datetime.now)  # 添加时间
    comments = db.relationship("Comment", backref="movie")  # 评论外键关系关联
    movie_cols = db.relationship("MovieCol", backref="movie")  # 收藏外键关系关联

    def __repr__(self):
        return "<Movie {}>".format(self.title)


# 预告
class Preview(db.Model):
    __tablename__ = "preview"
    id = db.Column(db.Integer, primary_key=True)  # 编号
    title = db.Column(db.String(255), unique=True)  # 标题
    cover = db.Column(db.String(255), unique=True)  # 封面
    addtime = db.Column(db.DateTime, index=True,
                        default=datetime.now)  # 添加时间

    def __repr__(self):
        return "<Preview {}>".format(self.title)


# 评论
class Comment(db.Model):
    __tablename__ = "comment"
    id = db.Column(db.Integer, primary_key=True)  # 编号
    content = db.Column(db.Text)  # 内容
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))  # 所属会员
    movie_id = db.Column(db.Integer, db.ForeignKey("movie.id"))  # 所属电影
    addtime = db.Column(db.DateTime, index=True,
                        default=datetime.now)  # 添加时间

    def __repr__(self):
        return "<Comment {}>".format(self.id)


# 电影收藏
class MovieCol(db.Model):
    __tablename__ = "movieCol"
    id = db.Column(db.Integer, primary_key=True)  # 编号
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))  # 所属会员
    movie_id = db.Column(db.Integer, db.ForeignKey("movie.id"))  # 所属电影
    addtime = db.Column(db.DateTime, index=True,
                        default=datetime.now)  # 添加时间

    def __repr__(self):
        return "<MovieCol {}>".format(self.id)


# 权限
class Auth(db.Model):
    __tablename__ = "auth"
    id = db.Column(db.Integer, primary_key=True)  # 编号
    name = db.Column(db.String(255), unique=True)  # 名称
    url = db.Column(db.String(255), unique=True)  # 地址
    addtime = db.Column(db.DateTime, index=True,
                        default=datetime.now)  # 添加时间

    def __repr__(self):
        return "<Auth {}>".format(self.name)


# 角色
class Role(db.Model):
    __tablename__ = "role"
    id = db.Column(db.Integer, primary_key=True)  # 编号
    name = db.Column(db.String(255), unique=True)  # 名称
    auths = db.Column(db.String(600))  # 权限地址
    addtime = db.Column(db.DateTime, index=True,
                        default=datetime.now)  # 添加时间
    admins = db.relationship("Admin", backref="role")  # 管理员关系外键

    def __repr__(self):
        return "<Role {}>".format(self.name)


# 管理员
class Admin(db.Model):
    __tablename__ = "admin"
    id = db.Column(db.Integer, primary_key=True)  # 编号
    name = db.Column(db.String(100), unique=True)  # 管理员账号
    pwd = db.Column(db.String(100))  # 管理员密码
    is_super = db.Column(db.SmallInteger)  # 是否为超级管理员, 0代表为超级管理员
    role_id = db.Column(db.Integer, db.ForeignKey("role.id"))  # 所属角色
    addtime = db.Column(db.DateTime, index=True,
                        default=datetime.now)  # 添加时间
    admin_logs = db.relationship("AdminLog", backref="admin")  # 管理员登录日志关系外键
    op_logs = db.relationship("OpLog", backref="admin")  # 管理员操作日志关系外键

    def __repr__(self):
        return "<Admin {}>".format(self.name)

    def check_pwd(self, pwd):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.pwd, pwd)


# 管理员日志
class AdminLog(db.Model):
    __tablename__ = "adminLog"
    id = db.Column(db.Integer, primary_key=True)  # 编号
    admin_id = db.Column(db.Integer, db.ForeignKey("admin.id"))  # 所属管理员
    ip = db.Column(db.String(100))  # 登录IP
    addtime = db.Column(db.DateTime, index=True,
                        default=datetime.now)  # 登录时间

    def __repr__(self):
        return "<AdminLog {}>".format(self.id)


# 管理员操作日志
class OpLog(db.Model):
    __tablename__ = "opLog"
    reason = db.Column(db.String(600))  # 操作原因
    id = db.Column(db.Integer, primary_key=True)  # 编号
    admin_id = db.Column(db.Integer, db.ForeignKey("admin.id"))  # 所属管理员
    ip = db.Column(db.String(100))  # 登录IP
    addtime = db.Column(db.DateTime, index=True,
                        default=datetime.now)  # 登录时间

    def __repr__(self):
        return "<OpLog {}>".format(self.id)


# if __name__ == '__main__':
#     # db.create_all()
#     from werkzeug.security import generate_password_hash
#
#     admin = Admin(
#         name="movie",
#         pwd=generate_password_hash("movie"),
#         is_super=0,
#         role_id=1
#     )
#     db.session.add(admin)
#     db.session.commit()
