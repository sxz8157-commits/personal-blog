"""在本机配置管理员；明文密码不会写入代码或终端日志。"""
import argparse
import getpass
import secrets
from pathlib import Path
from dotenv import dotenv_values
from werkzeug.security import generate_password_hash


def configure_admin(generate: bool):
    root = Path(__file__).resolve().parent.parent
    password = secrets.token_urlsafe(24) if generate else getpass.getpass('请输入新的管理密码（至少 12 字符）：')
    if len(password) < 12 or len(password) > 256:
        raise ValueError('密码长度需在 12–256 字符之间')
    env = {key: value or '' for key, value in dotenv_values(root / '.env').items() if key != 'VITE_ADMIN_PASSWORD'}
    env.update(SECRET_KEY=secrets.token_hex(32), ADMIN_PASSWORD_HASH=generate_password_hash(password))
    env.setdefault('APP_ENV', 'development')
    env.setdefault('SITE_URL', 'https://peixin.uno')
    env.setdefault('TRUST_PROXY', 'false')
    env.setdefault('CORS_ORIGINS', 'http://localhost:4000,http://127.0.0.1:4000')
    # 双引号与特殊字符使用 dotenv 支持的转义；不在日志打印配置值。
    def quoted(value):
        return '"' + value.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n') + '"'
    (root / '.env').write_text('\n'.join(f'{key}={quoted(value)}' for key, value in env.items()) + '\n', encoding='utf-8')
    private_file = root / 'backend' / '.admin-initial-password.txt'
    if generate:
        private_file.write_text('后台地址：/admin\n管理员密码：' + password + '\n请妥善保管此本地文件，不要提交或上传。\n', encoding='utf-8')
    elif private_file.exists():
        private_file.write_text('初始密码已失效，管理员密码已由用户重新设置。\n', encoding='utf-8')
    print('管理员配置完成。' + ('初始密码保存在 backend/.admin-initial-password.txt。' if generate else '旧会话已失效。'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='配置博客管理员并轮换会话密钥')
    parser.add_argument('command', choices=['configure-admin'])
    parser.add_argument('--generate', action='store_true', help='生成随机密码并写入本地私有文件')
    args = parser.parse_args()
    configure_admin(args.generate)
