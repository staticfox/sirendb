from flask import make_response, request
from flask_login import login_user
from werkzeug.security import check_password_hash

from sirendb.models.user import User

from .. import auth_endpoints


@auth_endpoints.route('/api/v1/auth/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    if not username or not password:
        return abort(401)

    user = User.query.filter_by(username=username).one_or_none()
    if not user:
        return abort(401)

    if not check_password_hash(user.password_hash, password):
        return abort(401)

    login_user(user)

    # return redirect(... webapp url ...)
    return make_response({
        'ok': True
    })
