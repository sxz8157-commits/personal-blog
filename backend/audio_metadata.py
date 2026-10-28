"""只读获取音频文字标签和内嵌封面，不改写原音频。"""
import base64
import binascii
import io
import logging
import re
from functools import lru_cache
from pathlib import Path
from typing import Iterator

from mutagen import File, MutagenError, Tags
from mutagen.flac import Picture
from mutagen.id3 import ID3
from PIL import Image, UnidentifiedImageError

logger = logging.getLogger(__name__)
_UNKNOWN_ARTIST = '未知艺术家'
_CACHE_SIZE = 256
MAX_COVER_BYTES = 5 * 1024 * 1024
_MAX_COVER_PIXELS = 40_000_000
_COVER_MIME_TYPES = {
    'JPEG': 'image/jpeg', 'PNG': 'image/png', 'WEBP': 'image/webp',
    'GIF': 'image/gif', 'BMP': 'image/bmp',
}


def _filename_metadata(filepath: Path) -> tuple[str, str]:
    """兼容原始“歌名 - 作者”和上传后的“歌名_-_作者”命名。"""
    stem = filepath.stem
    parts = re.split(r'\s+-\s+|_-_', stem, maxsplit=1)
    title = parts[0].replace('_', ' ').strip() or stem or '未知曲目'
    artist = parts[1].replace('_', ' ').strip() if len(parts) == 2 else ''
    # 清理仅由分隔符构成的作者占位，不根据歌名猜测作者。
    if not artist.strip(' -'):
        artist = _UNKNOWN_ARTIST
    return title, artist


def _text_values(value: object) -> list[str]:
    """只使用有效文字，保留 Mutagen 解码后的 Unicode 与多值信息。"""
    values = [value] if isinstance(value, str) else value
    if not isinstance(values, (list, tuple)):
        return []
    return [text for item in values if isinstance(item, str)
            if (text := item.replace('\x00', '').strip())]


def _tag_values(tags: Tags | None, key: str) -> list[str]:
    if tags is None:
        return []
    if isinstance(tags, ID3):
        # WAV 等格式仍返回原始 ID3；只取文字帧，不处理封面。
        frame = tags.get('TIT2' if key == 'title' else 'TPE1')
        return _text_values(getattr(frame, 'text', None))
    return _text_values(tags.get(key))


@lru_cache(maxsize=_CACHE_SIZE)
def _read_cached(absolute_path: str, mtime_ns: int, size: int) -> tuple[str, str]:
    """时间戳和大小参与缓存键，覆盖文件后自动读取新标签。"""
    fallback_title, fallback_artist = _filename_metadata(Path(absolute_path))
    try:
        audio = File(absolute_path, easy=True)
        tags = audio.tags if audio is not None else None
        titles = _tag_values(tags, 'title')
        artists = _tag_values(tags, 'artist')
        return (titles[0] if titles else fallback_title,
                '、'.join(artists) if artists else fallback_artist)
    except (MutagenError, OSError, ValueError, EOFError) as error:
        # 单个损坏或不可读文件不影响其他曲目；缓存也避免重复警告。
        logger.warning('读取音频标签失败，使用文件名回退：%s（%s）', absolute_path, error)
        return fallback_title, fallback_artist


def read_audio_metadata(filepath: str | Path) -> tuple[str, str]:
    """返回 (歌名, 艺术家)，只读标签，不改写音频或返回图片。"""
    path = Path(filepath)
    try:
        path = path.resolve()
        stat = path.stat()
    except OSError as error:
        logger.warning('无法访问音频文件，使用文件名回退：%s（%s）', path, error)
        return _filename_metadata(path)
    return _read_cached(str(path), stat.st_mtime_ns, stat.st_size)


def _decode_picture_value(value: object) -> bytes | None:
    """先限制 base64 长度，再解码 Vorbis 封面，避免超大标签分配。"""
    if not isinstance(value, str) or len(value) > 4 * ((MAX_COVER_BYTES + 2) // 3):
        return None
    try:
        decoded = base64.b64decode(value, validate=True)
    except (ValueError, binascii.Error):
        return None
    return decoded if len(decoded) <= MAX_COVER_BYTES else None


def _embedded_pictures(audio: object) -> Iterator[bytes]:
    """按常见容器读取封面；ID3/FLAC 优先封面正面（类型 3）。"""
    tags = getattr(audio, 'tags', None)
    if isinstance(tags, ID3):
        frames = sorted(tags.getall('APIC'), key=lambda frame: frame.type != 3)
        for frame in frames:
            yield frame.data

    pictures = getattr(audio, 'pictures', [])
    for picture in sorted(pictures, key=lambda picture: picture.type != 3):
        yield picture.data

    if tags is None or isinstance(tags, ID3):
        return
    # MP4 的 covr 是原始图片字节；格式字段仅作容器提示，实际 MIME 在后面验证。
    for value in tags.get('covr', []):
        if isinstance(value, bytes):
            yield value
    for value in tags.get('metadata_block_picture', []):
        block = _decode_picture_value(value)
        if block is None:
            continue
        try:
            yield Picture(block).data
        except (MutagenError, ValueError, EOFError) as error:
            logger.warning('忽略损坏的 Vorbis 封面标签：%s', error)
    # 兼容早期 Vorbis coverart 标签。
    for value in tags.get('coverart', []):
        data = _decode_picture_value(value)
        if data is not None:
            yield data


def _verified_cover(data: bytes) -> tuple[bytes, str] | None:
    """只返回实际可识别的栅格图片，不信任标签声明的 MIME 或图片 URL。"""
    if not data or len(data) > MAX_COVER_BYTES:
        return None
    try:
        with Image.open(io.BytesIO(data)) as image:
            mimetype = _COVER_MIME_TYPES.get(image.format)
            if not mimetype or image.width * image.height > _MAX_COVER_PIXELS:
                return None
            image.verify()
        return data, mimetype
    except (UnidentifiedImageError, OSError, SyntaxError, ValueError,
            Image.DecompressionBombError):
        return None


def read_audio_cover(filepath: str | Path) -> tuple[bytes, str] | None:
    """返回 (原始封面字节, 实际 MIME)，缺失/损坏/过大时返回 None。

    图片仅在独立封面请求中解析，不放进歌曲列表或进程缓存。
    """
    path = Path(filepath)
    try:
        audio = File(path, easy=False)
        if audio is None:
            return None
        for data in _embedded_pictures(audio):
            cover = _verified_cover(data)
            if cover is not None:
                return cover
        return None
    except (MutagenError, OSError, ValueError, EOFError) as error:
        logger.warning('读取音频封面失败：%s（%s）', path, error)
        return None
