"""隔离数据库与文件目录，验证后台权限、内容持久化和上传链路。"""
import io
import os
import secrets
import tempfile
import unittest
import wave
from unittest.mock import patch
from pathlib import Path
from urllib.parse import quote
from xml.etree import ElementTree

from werkzeug.security import generate_password_hash
from PIL import Image
from mutagen.id3 import TIT2, TPE1, APIC
from mutagen.wave import WAVE

_temporary = tempfile.TemporaryDirectory(prefix='blog-api-tests-')
_root = Path(_temporary.name).resolve()
_password = secrets.token_urlsafe(24)
os.environ.update(DATABASE_URL='sqlite:///' + str(_root / 'test.db'), PUBLIC_DIR=str(_root / 'public'),
                  SECRET_KEY=secrets.token_hex(32), ADMIN_PASSWORD_HASH=generate_password_hash(_password),
                  APP_ENV='production', TRUST_PROXY='true', CORS_ORIGINS='https://localhost')
from backend.app import app, db, Article, Category, Card, AboutContent, Comment, init_db
from backend.security import _login_attempts
from backend.uploads import safe_filename, public_path


class AdminTests(unittest.TestCase):
    def setUp(self):
        app.config.update(TESTING=True, MAX_CONTENT_LENGTH=105 * 1024 * 1024, ADMIN_PASSWORD_HASH=generate_password_hash(_password))
        self.context = app.app_context()
        self.context.push()
        # 仅允许清理此测试创建的数据库。
        self.assertTrue(Path(db.engine.url.database).resolve().is_relative_to(_root))
        db.session.remove()
        db.drop_all()
        db.create_all()
        _login_attempts.clear()
        self.client = app.test_client()
        self.token = ''

    @classmethod
    def tearDownClass(cls):
        with app.app_context():
            db.session.remove()
            db.engine.dispose()
        _temporary.cleanup()

    def tearDown(self):
        db.session.remove()
        self.context.pop()

    def call(self, method, url, **kwargs):
        return self.client.open(url, method=method, base_url='https://localhost', **kwargs)

    def login(self):
        response = self.call('POST', '/api/admin/login', json={'password': _password})
        self.assertEqual(response.status_code, 200)
        self.token = response.json['csrf_token']
        return response

    def write(self, method, url, **kwargs):
        return self.call(method, url, headers={'X-CSRF-Token': self.token}, **kwargs)

    def test_all_admin_writes_require_auth_and_csrf(self):
        routes = [('POST','/api/cards'),('PUT','/api/cards/1'),('DELETE','/api/cards/1'),('POST','/api/cards/seed'),
                  ('POST','/api/about'),('PUT','/api/about/1'),('DELETE','/api/about/1'),('POST','/api/about/seed'),
                  ('POST','/api/admin/articles'),('PUT','/api/admin/articles/1'),('DELETE','/api/admin/articles/1'),
                  ('PUT','/api/admin/pages/home'),('PUT','/api/admin/about'),('POST','/api/admin/upload'),
                  ('DELETE','/api/admin/file/wenz/a.md'),('PUT','/api/admin/documents/a.md'),('DELETE','/api/admin/comments/1')]
        for method, url in routes:
            with self.subTest(url=url, method=method): self.assertEqual(self.call(method,url,json={}).status_code,401)
        response = self.login()
        cookie = response.headers['Set-Cookie']
        self.assertIn('HttpOnly',cookie); self.assertIn('Secure',cookie); self.assertIn('SameSite=Lax',cookie)
        for method,url in routes:
            with self.subTest(url=url, method=method): self.assertEqual(self.call(method,url,json={}).status_code,403)
        self.assertEqual(self.call('POST','/api/cards',json={},headers={'X-CSRF-Token':'非法'}).status_code,403)
        self.assertEqual(self.call('GET','/api/admin/session').headers['Cache-Control'],'no-store')
        self.assertEqual(self.write('POST','/api/admin/logout').status_code,200)
        self.assertEqual(self.call('GET','/api/admin/articles').status_code,401)

    def test_login_rate_limit_origin_and_rotation(self):
        self.assertEqual(self.call('POST','/api/admin/login',json={'password':_password},headers={'Origin':'https://evil.example'}).status_code,403)
        self.login()
        app.config['ADMIN_PASSWORD_HASH'] = generate_password_hash(secrets.token_urlsafe(24))
        self.assertEqual(self.call('GET','/api/admin/articles').status_code,401)
        _login_attempts.clear()
        for _ in range(5): self.assertEqual(self.call('POST','/api/admin/login',json={'password':'invalid'}).status_code,401)
        self.assertEqual(self.call('POST','/api/admin/login',json={'password':'invalid'}).status_code,429)

    def test_article_draft_publish_unpublish_and_delete(self):
        self.login()
        payload={'title':'验证文章 ]]>','content':'# 标题\n\n正文','is_published':False}
        created=self.write('POST','/api/admin/articles',json=payload)
        self.assertEqual(created.status_code,201); identifier=created.json['article']['id']
        self.assertEqual(self.call('GET',f'/api/articles/{identifier}').status_code,404)
        self.assertEqual(self.call('POST',f'/api/articles/{identifier}/like').status_code,404)
        self.assertEqual(self.call('POST','/api/comments',json={'article_id':identifier}).status_code,404)
        self.assertEqual(self.call('GET','/api/article-index').json['total'],0)
        self.assertEqual(self.call('GET',f'/api/admin/articles/{identifier}').json['article']['content'],payload['content'])
        payload['is_published']=True
        self.assertEqual(self.write('PUT',f'/api/admin/articles/{identifier}',json=payload).status_code,200)
        self.assertEqual(self.call('GET',f'/api/articles/{identifier}').json['content'],payload['content'])
        self.assertIn(f'db-{identifier}',[a['id'] for a in self.call('GET','/api/article-index').json['articles']])
        for url in ['/feed.xml','/sitemap.xml']: ElementTree.fromstring(self.call('GET',url).data)
        payload['is_published']=False
        self.write('PUT',f'/api/admin/articles/{identifier}',json=payload)
        self.assertEqual(self.call('GET',f'/api/articles/{identifier}').status_code,404)
        db.session.add(Comment(article_id=identifier,author_name='测试',author_email='test@example.test',content='测试评论内容'));db.session.commit()
        self.assertEqual(self.write('DELETE',f'/api/admin/articles/{identifier}').status_code,200)
        self.assertEqual(Comment.query.count(),0)
        self.assertEqual(self.call('GET',f'/api/admin/articles/{identifier}').status_code,404)

    def test_page_and_about_save_validation_persistence(self):
        init_db(); self.login()
        result=self.write('PUT','/api/admin/pages/home',json={'title':'我的首页','subtitle':'你好'})
        self.assertEqual(result.status_code,200)
        about={'intro':{'name':'测试名字','subtitle':'','bio':'测试简介'},'tags':['标签'],'skills':['技能'],'contact':{'email':'','github':''}}
        self.assertEqual(self.write('PUT','/api/admin/about',json=about).status_code,200)
        card=Card.query.first();card.title='保留卡片';db.session.commit();card_id=card.id
        before=(AboutContent.query.count(),Card.query.count(),Article.query.count())
        init_db();db.session.expire_all()
        self.assertEqual(before,(AboutContent.query.count(),Card.query.count(),Article.query.count()))
        self.assertEqual(db.session.get(Card,card_id).title,'保留卡片')
        self.assertEqual(self.call('GET','/api/pages').json['pages']['home']['title'],'我的首页')
        self.assertEqual(self.call('GET','/api/about').json['intro'][0]['value'],'测试名字')
        cleared={**about,'tags':[],'skills':[]}
        self.assertEqual(self.write('PUT','/api/admin/about',json=cleared).status_code,200)
        self.assertEqual(self.call('GET','/api/about').json['skills'],[])
        invalid={**about,'tags':[{'not':'text'}]}
        self.assertEqual(self.write('PUT','/api/admin/about',json=invalid).status_code,400)
        self.assertEqual(self.call('GET','/api/about').json['intro'][0]['value'],'测试名字')
        self.assertEqual(self.write('PUT','/api/admin/pages/home',json={'unknown':'x'}).status_code,400)

    def test_upload_read_edit_delete_and_content_rejection(self):
        self.assertEqual(safe_filename('Linux（Ubuntu）.docx'), 'Linux（Ubuntu）.docx')
        text_path = _root / 'public' / 'wenz' / '全角（文件）.txt'
        text_path.parent.mkdir(parents=True, exist_ok=True)
        text_path.write_text('<b>纯文本</b>', encoding='utf-8')
        self.assertEqual(public_path(str(_root / 'public'), 'wenz', text_path.name), text_path)
        self.assertEqual(self.call('GET', '/api/md-articles/' + text_path.name).json['file_type'], 'txt')

        self.login()
        image=io.BytesIO();Image.new('RGB',(2,2)).save(image,format='PNG');image.seek(0)
        result=self.write('POST','/api/admin/upload',data={'subdir':'tupian','files':[(image,'中文图片.png'),(io.BytesIO(b'<html>bad</html>'),'fake.png')]})
        self.assertEqual(result.status_code,201);self.assertEqual(result.json['count'],1);self.assertEqual(len(result.json['rejected']),1)
        filename=result.json['uploaded'][0]
        self.assertTrue(filename.startswith('中文图片'))
        self.assertEqual(result.json['files'], [{'filename': filename, 'url': '/api/files/tupian/' + quote(filename)}])
        response=self.call('GET','/api/files/tupian/'+filename)
        self.assertEqual(response.status_code,200); response.close()
        uploaded=self.write('POST','/api/admin/upload',data={'subdir':'wenz','files':(io.BytesIO('# 文章\n正文'.encode()),'测试.md')})
        self.assertEqual(uploaded.status_code,201)
        name=uploaded.json['uploaded'][0]
        self.assertEqual(uploaded.json['files'], [{'filename': name, 'url': '/api/files/wenz/' + quote(name)}])
        self.assertIn(name,[a['filename'] for a in self.call('GET','/api/md-articles').json['articles']])
        self.assertEqual(self.write('PUT','/api/admin/documents/'+name,json={'content':'# 修改后正文'}).status_code,200)
        self.assertEqual(self.call('GET','/api/md-articles/'+name).json['content'],'# 修改后正文')
        self.assertEqual(self.write('DELETE','/api/admin/file/wenz/'+name).status_code,200)
        self.assertEqual(self.call('GET','/api/files/wenz/'+name).status_code,404)
        self.assertIn(self.write('DELETE','/api/admin/file/wenz/%2e%2e%5cblog.db').status_code,(400,404))
        app.config['MAX_CONTENT_LENGTH']=32
        self.assertEqual(self.write('POST','/api/admin/upload',data={'subdir':'wenz','files':(io.BytesIO(b'x'*100),'a.md')}).status_code,413)

    def test_dangerous_urls_and_invalid_inputs_rejected(self):
        self.login()
        self.assertEqual(self.write('POST','/api/cards',json={'title':'测试','card_type':'intro','link':'javascript:alert(1)'}).status_code,400)
        self.assertEqual(self.write('POST','/api/cards',json={'title':['bad'],'card_type':'intro'}).status_code,400)
        self.assertEqual(self.write('POST','/api/admin/articles',json={'title':'测试','content':'正文','is_published':'false'}).status_code,400)
        self.assertEqual(self.call('GET','/api/articles?per_page=-1&page=-1').status_code,200)
        self.assertNotIn('Access-Control-Allow-Origin',self.call('GET','/api/pages',headers={'Origin':'https://evil.example'}).headers)

    @staticmethod
    def cover_bytes(image_format='PNG', color='red'):
        image = io.BytesIO()
        Image.new('RGB', (4, 4), color).save(image, format=image_format)
        return image.getvalue()

    def test_cover_upload_returns_readable_url_and_compatible_success_fields(self):
        self.login()
        rules = self.call('GET', '/api/admin/upload-rules').json
        self.assertEqual(set(rules['extensions']['covers']), {'.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp'})
        self.assertEqual(rules['image_limit_mb'], 5)
        self.assertEqual(rules['cover_limit_mb'], 5)
        original = self.cover_bytes()
        filename = '中文封面 （测试）.png'
        result = self.write('POST', '/api/admin/upload', data={'subdir': 'covers', 'files': [
            (io.BytesIO(original), filename), (io.BytesIO(b'<html>bad</html>'), '伪造封面.png')]})
        self.assertEqual(result.status_code, 201)
        self.assertEqual(result.json['count'], 1)
        self.assertEqual(result.json['uploaded'], [filename])
        self.assertEqual(result.json['files'], [{'filename': filename, 'url': '/api/files/covers/' + quote(filename)}])
        self.assertEqual(len(result.json['rejected']), 1)
        self.assertEqual(result.json['rejected'][0]['filename'], '伪造封面.png')
        url = result.json['files'][0]['url']
        response = self.call('GET', url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, original)
        self.assertEqual(response.mimetype, 'image/png')
        self.assertEqual(response.headers['X-Content-Type-Options'], 'nosniff')
        self.assertEqual(response.headers['Cache-Control'], 'public, max-age=3600')
        self.assertTrue(response.headers['Content-Disposition'].startswith('inline'))
        response.close()
        head = self.call('HEAD', url)
        self.assertEqual(head.status_code, 200)
        self.assertEqual(head.data, b'')
        head.close()
        backgrounds = self.call('GET', '/api/background-media').json
        self.assertNotIn(filename, str(backgrounds))
        self.assertEqual(self.call('GET', '/api/files/covers/不存在.png').status_code, 404)

    def test_cover_duplicate_keeps_original_and_returns_actual_new_filename(self):
        self.login()
        filename = '重复封面.png'
        first_bytes = self.cover_bytes(color='red')
        first = self.write('POST', '/api/admin/upload', data={'subdir': 'covers', 'files': (io.BytesIO(first_bytes), filename)})
        second_bytes = self.cover_bytes(color='blue')
        second = self.write('POST', '/api/admin/upload', data={'subdir': 'covers', 'files': (io.BytesIO(second_bytes), filename)})
        self.assertEqual((first.status_code, second.status_code), (201, 201))
        second_name = second.json['uploaded'][0]
        self.assertNotEqual(second_name, filename)
        self.assertTrue(second_name.startswith('重复封面_'))
        self.assertEqual(second.json['files'], [{'filename': second_name, 'url': '/api/files/covers/' + quote(second_name)}])
        for response, expected in ((first, first_bytes), (second, second_bytes)):
            image = self.call('GET', response.json['files'][0]['url'])
            self.assertEqual(image.data, expected)
            image.close()

    def test_long_chinese_cover_name_uploads_reads_and_saves_article(self):
        self.login()
        original_filename = '长中文封面' * 36 + '.png'
        self.assertLessEqual(len(original_filename), 200)
        self.assertGreater(len(original_filename.encode('utf-8')), 255)
        self.assertGreater(len('/api/files/covers/' + quote(original_filename)), 500)
        original_bytes = self.cover_bytes()
        uploaded = self.write('POST', '/api/admin/upload', data={'subdir': 'covers',
            'files': (io.BytesIO(original_bytes), original_filename)})
        self.assertEqual(uploaded.status_code, 201)
        filename = uploaded.json['uploaded'][0]
        self.assertRegex(filename, r'^cover_[0-9a-f]{32}\.png$')
        self.assertLessEqual(len(filename.encode('utf-8')), 255)
        self.assertEqual(uploaded.json['files'][0]['filename'], filename)
        cover_url = uploaded.json['files'][0]['url']
        self.assertEqual(cover_url, '/api/files/covers/' + quote(filename))
        self.assertLessEqual(len(cover_url), 500)
        image = self.call('GET', cover_url)
        self.assertEqual(image.status_code, 200)
        self.assertEqual(image.data, original_bytes)
        image.close()
        created = self.write('POST', '/api/admin/articles', json={'title': '长文件名封面验证',
            'content': '# 正文', 'cover_image': cover_url, 'is_published': False})
        self.assertEqual(created.status_code, 201)
        identifier = created.json['article']['id']
        self.assertEqual(self.call('GET', f'/api/admin/articles/{identifier}').json['article']['cover_image'], cover_url)

        # 原名接近地址上限时，重名后缀也不能让下一张封面无法保存。
        boundary_filename = 'a' * 113 + '中' * 40 + '.png'
        self.assertEqual(len('/api/files/covers/' + quote(boundary_filename)), 495)
        first = self.write('POST', '/api/admin/upload', data={'subdir': 'covers',
            'files': (io.BytesIO(original_bytes), boundary_filename)})
        second = self.write('POST', '/api/admin/upload', data={'subdir': 'covers',
            'files': (io.BytesIO(original_bytes), boundary_filename)})
        self.assertEqual((first.status_code, second.status_code), (201, 201))
        self.assertEqual(first.json['uploaded'], [boundary_filename])
        self.assertRegex(second.json['uploaded'][0], r'^cover_[0-9a-f]{32}\.png$')
        second_url = second.json['files'][0]['url']
        self.assertLessEqual(len(second_url), 500)
        saved = self.write('PUT', f'/api/admin/articles/{identifier}', json={'title': '重名封面验证',
            'content': '# 正文', 'cover_image': second_url, 'is_published': False})
        self.assertEqual(saved.status_code, 200)
        self.assertEqual(saved.json['article']['cover_image'], second_url)

    def test_cover_all_supported_raster_formats_have_correct_mime(self):
        self.login()
        formats = {'.jpg': ('JPEG', 'image/jpeg'), '.jpeg': ('JPEG', 'image/jpeg'),
                   '.png': ('PNG', 'image/png'), '.webp': ('WEBP', 'image/webp'),
                   '.gif': ('GIF', 'image/gif'), '.bmp': ('BMP', 'image/bmp')}
        for extension, (image_format, mimetype) in formats.items():
            with self.subTest(extension=extension):
                uploaded = self.write('POST', '/api/admin/upload', data={'subdir': 'covers',
                    'files': (io.BytesIO(self.cover_bytes(image_format)), '格式封面' + extension)})
                self.assertEqual(uploaded.status_code, 201)
                image = self.call('GET', uploaded.json['files'][0]['url'])
                self.assertEqual(image.status_code, 200)
                self.assertEqual(image.mimetype, mimetype)
                image.close()

    def test_cover_upload_rejects_types_content_size_and_pixel_limits(self):
        self.login()
        invalid = [(b'<svg></svg>', '禁止.svg'), (b'\x00\x00\x00\x18ftypisom', '禁止.mp4'),
                   (b'<html>bad</html>', '禁止.png'), (self.cover_bytes('JPEG'), '格式错误.png'),
                   (b'\x00' * (5 * 1024 * 1024 + 1), '过大.png'), (b'', '空图片.png')]
        for data, filename in invalid:
            with self.subTest(filename=filename):
                response = self.write('POST', '/api/admin/upload', data={'subdir': 'covers', 'files': (io.BytesIO(data), filename)})
                self.assertEqual(response.status_code, 400)
                self.assertEqual(response.json['count'], 0)
                self.assertEqual(response.json['uploaded'], [])
                self.assertEqual(response.json['files'], [])
                self.assertEqual(response.json['rejected'][0]['filename'], filename)
                self.assertFalse((_root / 'public' / 'covers' / filename).exists())
                response.close()
                response.request.close()
                response.request.environ['wsgi.input'].close()
        # 隔离尺寸上限分支，不分配 4000 万像素图片内存。
        with patch('backend.uploads.Image.open') as image_open:
            image = image_open.return_value.__enter__.return_value
            image.format, image.width, image.height = 'PNG', 40_000_001, 1
            response = self.write('POST', '/api/admin/upload', data={'subdir': 'covers',
                'files': (io.BytesIO(self.cover_bytes()), '像素过大.png')})
            self.assertEqual(response.status_code, 400)
            self.assertIn('尺寸过大', response.json['rejected'][0]['reason'])
            image.verify.assert_not_called()

    def test_cover_upload_preserves_auth_csrf_and_rejects_cross_directory_paths(self):
        data = {'subdir': 'covers', 'files': (io.BytesIO(self.cover_bytes()), '权限封面.png')}
        self.assertEqual(self.call('POST', '/api/admin/upload', data=data).status_code, 401)
        self.login()
        data = {'subdir': 'covers', 'files': (io.BytesIO(self.cover_bytes()), '权限封面.png')}
        self.assertEqual(self.call('POST', '/api/admin/upload', data=data).status_code, 403)
        # Werkzeug 解析 multipart 引号中的反斜杠转义，文件名校验本身另行验证。
        with self.assertRaises(ValueError):
            safe_filename('..\\wenz\\跨目录.png')
        for filename in ('../tupian/跨目录.png', 'child/跨目录.png', 'CON.png'):
            with self.subTest(filename=filename):
                response = self.write('POST', '/api/admin/upload', data={'subdir': 'covers',
                    'files': (io.BytesIO(self.cover_bytes()), filename)})
                self.assertEqual(response.status_code, 400)
                self.assertEqual(response.json['files'], [])
        response = self.write('POST', '/api/admin/upload', data={'subdir': 'covers/../tupian',
            'files': (io.BytesIO(self.cover_bytes()), '跨目录.png')})
        self.assertEqual(response.status_code, 400)
        for filename in ('%2e%2e%2fwenz%2fsecret.png', '..%5csecret.png', 'child%2fsecret.png', 'CON.png'):
            with self.subTest(filename=filename):
                self.assertIn(self.call('GET', '/api/files/covers/' + filename).status_code, (400, 404))
        forbidden = _root / 'public' / 'covers' / '拒绝读取.svg'
        forbidden.parent.mkdir(parents=True, exist_ok=True)
        forbidden.write_bytes(b'<svg></svg>')
        self.assertEqual(self.call('GET', '/api/files/covers/' + quote(forbidden.name)).status_code, 404)

    def test_article_keeps_existing_cover_reference_and_clear_does_not_delete_media(self):
        self.login()
        uploaded = self.write('POST', '/api/admin/upload', data={'subdir': 'covers',
            'files': (io.BytesIO(self.cover_bytes()), '引用封面.png')})
        cover_url = uploaded.json['files'][0]['url']
        payload = {'title': '封面兼容文章', 'content': '# 正文', 'cover_image': cover_url, 'is_published': False}
        created = self.write('POST', '/api/admin/articles', json=payload)
        self.assertEqual(created.status_code, 201)
        identifier = created.json['article']['id']
        self.assertEqual(self.call('GET', f'/api/admin/articles/{identifier}').json['article']['cover_image'], cover_url)
        for reference in ('https://example.test/existing-cover.jpg', '/api/files/tupian/旧封面.png', ''):
            payload['cover_image'] = reference
            response = self.write('PUT', f'/api/admin/articles/{identifier}', json=payload)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json['article']['cover_image'], reference)
        image = self.call('GET', cover_url)
        self.assertEqual(image.status_code, 200)
        image.close()

    def test_audio_metadata_is_public_and_keeps_original_files(self):
        # 有效 WAV 加 UTF-16 标签，验证实际读取和原播放地址，无需管理权限。
        assets = _root / 'public' / 'assets'
        assets.mkdir(parents=True, exist_ok=True)
        tagged = assets / '-_.wav'
        with wave.open(str(tagged), 'wb') as audio:
            audio.setnchannels(1)
            audio.setsampwidth(2)
            audio.setframerate(8000)
            audio.writeframes(b'\x00\x00' * 800)
        metadata = WAVE(tagged)
        metadata.add_tags()
        metadata.tags.add(TIT2(encoding=1, text=['悪魔の子']))
        metadata.tags.add(TPE1(encoding=1, text=['ヒグチアイ']))
        picture = io.BytesIO()
        Image.new('RGB', (4, 4), 'red').save(picture, format='PNG')
        cover = picture.getvalue()
        metadata.tags.add(APIC(mime='image/png', type=3, desc='', data=cover))
        metadata.save()
        before = tagged.read_bytes()
        (assets / '备用歌名_-_备用作者.mp3').write_bytes(b'invalid audio')
        with self.assertLogs('backend.audio_metadata', level='WARNING'):
            response = self.call('GET', '/api/audio-files')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['total'], 2)
        rows = {item['filename']: item for item in response.json['audios']}
        self.assertEqual(rows['-_.wav']['name'], '悪魔の子')
        self.assertEqual(rows['-_.wav']['artist'], 'ヒグチアイ')
        self.assertEqual(rows['-_.wav']['src'], '/api/files/assets/-_.wav')
        cover_url = rows['-_.wav']['cover']
        self.assertTrue(cover_url.startswith('/api/audio-cover/-_.wav?v='))
        artwork = self.call('GET', cover_url)
        self.assertEqual(artwork.status_code, 200)
        self.assertEqual(artwork.data, cover)
        self.assertEqual(artwork.headers['Content-Type'], 'image/png')
        self.assertEqual(artwork.headers['X-Content-Type-Options'], 'nosniff')
        self.assertEqual(artwork.headers['Cache-Control'], 'public, max-age=3600')
        etag = artwork.headers['ETag']
        self.assertNotIn('Content-Disposition', artwork.headers)
        with patch('backend.app.read_audio_cover') as cover_reader:
            cached = self.call('GET', cover_url, headers={'If-None-Match': etag})
            self.assertEqual(cached.status_code, 304)
            self.assertEqual(cached.data, b'')
            cover_reader.assert_not_called()
        head = self.call('HEAD', cover_url)
        self.assertEqual(head.status_code, 200)
        self.assertEqual(head.data, b'')
        self.assertEqual(head.headers['Content-Length'], str(len(cover)))
        fallback = rows['备用歌名_-_备用作者.mp3']
        self.assertEqual((fallback['name'], fallback['artist']), ('备用歌名', '备用作者'))
        self.assertEqual(tagged.read_bytes(), before)
        media = self.call('GET', rows['-_.wav']['src'])
        self.assertEqual(media.status_code, 200)
        self.assertEqual(media.data, before)
        media.close()

        # 文件更新后，旧 ETag 不能复用；不改变生产文件或现有数据库。
        metadata.tags.delall('APIC')
        new_picture = io.BytesIO()
        Image.new('RGB', (5, 5), 'blue').save(new_picture, format='PNG')
        metadata.tags.add(APIC(mime='image/png', type=3, desc='', data=new_picture.getvalue()))
        metadata.save()
        updated = self.call('GET', cover_url, headers={'If-None-Match': etag})
        self.assertEqual(updated.status_code, 200)
        self.assertEqual(updated.data, new_picture.getvalue())
        self.assertNotEqual(updated.headers['ETag'], etag)

    def test_audio_cover_rejects_bad_paths_types_and_missing_cover(self):
        assets = _root / 'public' / 'assets'
        assets.mkdir(parents=True, exist_ok=True)
        (assets / '没有封面.mp3').write_bytes(b'invalid audio')
        (assets / '不是音频.txt').write_bytes(b'not an audio file')
        self.addCleanup((assets / '没有封面.mp3').unlink, missing_ok=True)
        self.addCleanup((assets / '不是音频.txt').unlink, missing_ok=True)
        for filename in ('不存在.mp3', '不是音频.txt', '..%5cblog.db', 'CON.mp3'):
            with self.subTest(filename=filename):
                self.assertIn(self.call('GET', '/api/audio-cover/' + filename).status_code, (400, 404))
        with self.assertLogs('backend.audio_metadata', level='WARNING'):
            missing = self.call('GET', '/api/audio-cover/没有封面.mp3')
        self.assertEqual(missing.status_code, 404)
        self.assertEqual(missing.json['error'], 'NOT_FOUND')
        self.assertEqual(missing.headers['Cache-Control'], 'no-store')
        self.assertIn(self.call('GET', '/api/audio-cover/%2e%2e%2fblog.db').status_code, (400, 404))


if __name__ == '__main__':
    unittest.main(verbosity=2)
