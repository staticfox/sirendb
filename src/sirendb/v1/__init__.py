from flask import Blueprint

auth_endpoints = Blueprint('v1_auth', __name__)

from . import login
from . import logout
