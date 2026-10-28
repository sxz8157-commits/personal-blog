"""统一上传白名单、文件内容校验和路径检查。"""
import unicodedata
import zipfile
from pathlib import Path

from PIL import Image

UPLOAD_EXTENSIONS = {
    'tupian': {'.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp', '.mp4', '.webm', '.mov', '.m4v'},
    'assets': {'.mp3', '.wav', '.ogg', '.m4a', '.aac', '.flac'},
    'wenz': {'.md', '.txt', '.pdf', '.docx', '.pptx', '.xlsx', '.xmind'},
    'covers': {'.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp'},
}
VIDEO_EXTENSIONS = {'.mp4', '.webm', '.mov', '.m4v'}


def safe_filename(filename: str) -> str:
    original_filename = filename
    filename = unicodedata.normalize('NFKC', filename)
    if not filename or len(filename) > 200 or filename in ('.', '..'):
        raise ValueError('文件名为空或过长')
    if any(c in filename for c in '/\\:<>"|?*') or any(ord(c) < 32 for c in filename) or filename.endswith(('.', ' ')):
        raise ValueError('文件名包含非法字符')
    if filename.split('.')[0].upper() in {'CON', 'PRN', 'AUX', 'NUL', *{f'COM{i}' for i in range(1, 10)}, *{f'LPT{i}' for i in range(1, 10)}}:
        raise ValueError('文件名为系统保留名称')
    return original_filename


def public_path(public_dir: str, subdir: str, filename: str) -> Path:
    if subdir not in {*UPLOAD_EXTENSIONS, 'toux'}:
        raise ValueError('无效的目录')
    base = Path(public_dir).resolve()
    target = (base / subdir / safe_filename(filename)).resolve()
    if not target.is_relative_to(base / subdir):
        raise ValueError('非法文件路径')
    return target


def validate_file(file, subdir: str) -> tuple[str, int]:
    filename = safe_filename(file.filename)
    ext = Path(filename).suffix.lower()
    if ext not in UPLOAD_EXTENSIONS[subdir]:
        raise ValueError('不支持的文件类型')
    file.seek(0, 2)
    size = file.tell()
    file.seek(0)
    max_mb = 100 if ext in VIDEO_EXTENSIONS or subdir == 'wenz' else (50 if subdir == 'assets' else 5)
    if ext in ('.md', '.txt'):
        max_mb = 1
    if not size or size > max_mb * 1024 * 1024:
        raise ValueError(f'文件为空或超过 {max_mb}MB 限制')
    head = file.read(32)
    file.seek(0)
    try:
        if subdir in ('tupian', 'covers') and ext not in VIDEO_EXTENSIONS:
            expected = {'.jpg': 'JPEG', '.jpeg': 'JPEG', '.png': 'PNG', '.webp': 'WEBP', '.gif': 'GIF', '.bmp': 'BMP'}
            with Image.open(file.stream) as image:
                if image.format != expected[ext] or image.width * image.height > 40_000_000:
                    raise ValueError('图片格式不匹配或尺寸过大')
                image.verify()
        elif ext in ('.md', '.txt'):
            content = file.read().decode('utf-8-sig')
            if '\x00' in content:
                raise ValueError('文本文件包含二进制内容')
        elif ext in ('.docx', '.pptx', '.xlsx', '.xmind'):
            with zipfile.ZipFile(file.stream) as archive:
                info = archive.infolist()
                if len(info) > 2000 or sum(i.file_size for i in info) > 200 * 1024 * 1024:
                    raise ValueError('文档解压后过大')
                names = set(archive.namelist())
                required = {'.docx': 'word/document.xml', '.pptx': 'ppt/presentation.xml', '.xlsx': 'xl/workbook.xml'}
                if ext == '.xmind':
                    if not {'content.json', 'content.xml'} & names:
                        raise ValueError('无效的 XMind 文件')
                elif required[ext] not in names or '[Content_Types].xml' not in names:
                    raise ValueError('文档格式与扩展名不匹配')
        else:
            checks = {
                '.pdf': head.startswith(b'%PDF-'),
                '.mp3': head.startswith(b'ID3') or (len(head) >= 2 and head[0] == 255 and head[1] & 224 == 224),
                '.aac': len(head) >= 2 and head[0] == 255 and head[1] & 246 == 240,
                '.wav': head.startswith(b'RIFF') and head[8:12] == b'WAVE',
                '.ogg': head.startswith(b'OggS'), '.flac': head.startswith(b'fLaC'),
                '.webm': head.startswith(b'\x1aE\xdf\xa3'),
            }
            if ext in {'.m4a', '.mp4', '.mov', '.m4v'}:
                valid = head[4:8] in (b'ftyp', b'moov', b'wide')
            else:
                valid = checks.get(ext, False)
            if not valid:
                raise ValueError('文件内容与扩展名不匹配')
    except (UnicodeError, zipfile.BadZipFile, OSError, SyntaxError, Image.DecompressionBombError) as exc:
        raise ValueError('文件内容损坏或格式不正确') from exc
    finally:
        file.seek(0)
    return filename, size
