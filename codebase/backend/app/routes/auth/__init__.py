"""
Authentication blueprint initialization and shared components.
"""

from flask import Blueprint

bp = Blueprint('auth', __name__)

from .login import login_required

# Import all routes to register them with the blueprint
from . import login, register, password, profile

__all__ = ['bp', 'login_required']