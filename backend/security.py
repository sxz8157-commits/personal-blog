"""单管理员会话认证；所有管理请求在服务端校验。"""
import hashlib
import secrets
import time
from collections import deque
from datetime import timedelta
from functools import wraps
from threading import Lock
from urllib.parse import urlsplit

from flask import current_app, jsonify, request, session
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.security import check_password_hash

_login_attempts = {}
_login_lock = Lock()


def credentials_version() -> str:
    return hashlib.sha256(current_app.config.get('ADMIN_PASSWORD_HASH', '').encode()).hexdigest()


def authenticated() -> bool:
    return bool(session.get('admin') and session.get('credential_version') == credentials_version())


def require_admin(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if not authenticated():
            return jsonify(error='UNAUTHORIZED', message='请先登录后台'), 401
        if request.method not in ('GET', 'HEAD', 'OPTIONS'):
            supplied = request.headers.get('X-CSRF-Token', '')
            expected = session.get('csrf_token', '')
            if not supplied or not expected or not secrets.compare_digest(supplied.encode('utf-8'), expected.encode('utf-8')):
                return jsonify(error='CSRF_FAILED', message='会话校验失败，请刷新页面重新登录'), 403
        return f(*args, **kwargs)
    return wrapped


def validate_url(value: str, field: str = '链接') -> str:
    if not isinstance(value, str) or len(value) > 500:
        raise ValueError(f'{field}必须是长度不超过 500 的字符串')
    value = value.strip()
    if not value:
        return value
    if any(ord(char) < 32 for char in value) or '\\' in value:
        raise ValueError(f'{field}包含非法字符')
    parsed = urlsplit(value)
    if value.startswith('#') or (value.startswith('/') and not value.startswith('//')):
        return value
    if parsed.scheme.lower() not in ('http', 'https') or not parsed.netloc or parsed.username or parsed.password:
        raise ValueError(f'{field}仅支持 http、https 或站内路径')
    return value


def configure_security(app):
    import os
    production = os.getenv('APP_ENV', 'development') == 'production'
    app.config.update(
        SECRET_KEY=os.getenv('SECRET_KEY') or None,
        ADMIN_PASSWORD_HASH=os.getenv('ADMIN_PASSWORD_HASH', ''),
        SESSION_COOKIE_NAME='blog_admin',
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SECURE=production,
        SESSION_COOKIE_SAMESITE='Lax',
        PERMANENT_SESSION_LIFETIME=timedelta(hours=8),
        SESSION_REFRESH_EACH_REQUEST=False,
        MAX_CONTENT_LENGTH=105 * 1024 * 1024,
    )
    if os.getenv('TRUST_PROXY', 'false').lower() == 'true':
        # 仅用于后端绑定回环地址、前方只有一层可信 Nginx 的部署。
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)

    @app.after_request
    def security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        if request.path.startswith('/api/admin/') or request.path == '/api/admin':
            response.headers['Cache-Control'] = 'no-store'
        return response

    @app.route('/api/admin/session', methods=['GET'])
    def admin_session():
        if not authenticated():
            return jsonify(authenticated=False), 401
        return jsonify(authenticated=True, csrf_token=session['csrf_token'])

    @app.route('/api/admin/login', methods=['POST'])
    def admin_login():
        if not app.secret_key or not app.config['ADMIN_PASSWORD_HASH']:
            return jsonify(error='CONFIG_ERROR', message='请先配置服务器管理账户'), 503
        origin = request.headers.get('Origin')
        allowed = {request.host_url.rstrip('/'), *app.config.get('ADMIN_ALLOWED_ORIGINS', [])}
        if origin and origin.rstrip('/') not in allowed:
            return jsonify(error='FORBIDDEN_ORIGIN', message='不允许的登录来源'), 403
        ip = request.remote_addr or 'unknown'
        now = time.monotonic()
        with _login_lock:
            # 清理过期项，限制内存占用。部署只使用一个进程以共享限流状态。
            for key in list(_login_attempts):
                while _login_attempts[key] and now - _login_attempts[key][0] > 600:
                    _login_attempts[key].popleft()
                if not _login_attempts[key]:
                    del _login_attempts[key]
            if ip not in _login_attempts and len(_login_attempts) >= 4096:
                return jsonify(error='RATE_LIMITED', message='登录请求过多，请稍后重试'), 429
            attempts = _login_attempts.setdefault(ip, deque())
            if len(attempts) >= 5:
                return jsonify(error='RATE_LIMITED', message='登录过于频繁，请 10 分钟后重试'), 429
            attempts.append(now)
        data = request.get_json(silent=True)
        password = data.get('password') if isinstance(data, dict) else None
        if not isinstance(password, str) or len(password) > 256 or not check_password_hash(app.config['ADMIN_PASSWORD_HASH'], password):
            app.logger.warning('管理员登录失败，来源 IP：%s', ip)
            return jsonify(error='UNAUTHORIZED', message='密码错误'), 401
        session.clear()
        session.permanent = True
        session['admin'] = True
        session['credential_version'] = credentials_version()
        session['csrf_token'] = secrets.token_urlsafe(32)
        return jsonify(authenticated=True, csrf_token=session['csrf_token'])

    @app.route('/api/admin/logout', methods=['POST'])
    @require_admin
    def admin_logout():
        session.clear()
        return jsonify(message='已退出登录')
