from flask import Blueprint

auth_endpoints = Blueprint('v1_auth', __name__)

from . import auth
from . import mutations
from . import queries
from . import types
