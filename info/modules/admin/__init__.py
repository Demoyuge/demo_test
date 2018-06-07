from flask import Blueprint, session, redirect, url_for, request

admin_blue = Blueprint("admin",__name__,url_prefix='/admin')

from . import views


@admin_blue.before_request
def check_admin():
    is_admin = session.get('is_admin',False)

    if not is_admin and not request.url.endswith('/admin/login')and not request.url.endswith('/admin/user_count'):
        return redirect(url_for('index.index'))