from flask import make_response
from flask_login import logout_user

from . import auth_endpoints


@auth_endpoints.route('/api/v1/logout', methods=['GET'])
def logout():
    logout_user()

    # return redirect(... webapp url ...)
    return make_response({
        'ok': True
    })
