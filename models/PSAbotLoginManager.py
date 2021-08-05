from functools import wraps
from flask import session, redirect, url_for
from flask_login import LoginManager,UserMixin
from . import user

''' ------------------------------------------------------------
step1. import
    from models.PSAbotLoginManager import roles_required,login_required
    
step2. use decorater
    @login_required                                     # 使用者必須登入才可瀏覽，若未登入會導向登入畫面
    @roles_required('facebook_user', 'google_user')     # 使用者必須屬於其中一種類別才可瀏覽，若不屬於會導向登入畫面
------------------------------------------------------------ '''

class PSAbotLoginManager(LoginManager):
    def __init__(self, app):
        super().__init__()
        self.init_app(app)

# --------------- User class ---------------
class UserModel(UserMixin):  
    # -- 包含
        # -- property : is_active,is_authenticated,is_anonymous,role
        # -- method : get_id()
    
    def __init__(self, user_id):
        user_data = user.query_user(user_id)
        self.id = user_data['_id']  # 顏色屬性
        self.role = user_data['role']
    
    @property
    def is_manager(self):
        return False
# --------------- end ---------------

# 檢測使用者類別
def roles_required(*roles):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if session.get('role') not in roles:
                return redirect(url_for('login_web.login', _scheme="https", _external=True))
            return f(*args, **kwargs)
        return wrapped
    return wrapper

# 檢測是否登入
def login_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if session.get('user_id') is None:
            return redirect(url_for('login_web.login', _scheme="https", _external=True))
        return func(*args, **kwargs)
    return decorated_function
