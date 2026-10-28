"""在临时目录验证音频标签、文件名回退和有界缓存，不操作实际媒体。"""
import os
import base64
import io
import tempfile
import unittest
import wave
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from mutagen import MutagenError
from mutagen.easyid3 import EasyID3
from mutagen.flac import Picture
from mutagen.id3 import ID3, TIT2, TPE1, APIC
from mutagen.mp4 import MP4Cover
from mutagen.wave import WAVE
from PIL import Image

from backend.audio_metadata import MAX_COVER_BYTES, _read_cached, read_audio_metadata, read_audio_cover


class AudioMetadataTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='blog-audio-tests-')
        self.root = Path(self.temporary.name)
        _read_cached.cache_clear()

    def tearDown(self):
        _read_cached.cache_clear()
        self.temporary.cleanup()

    def make_file(self, name: str) -> Path:
        path = self.root / name
        path.write_bytes(b'temporary audio placeholder')
        return path

    def test_id3_utf16_title_and_artist_are_read_without_writing(self):
        path = self.make_file('-_.mp3')
        tags = ID3()
        tags.add(TIT2(encoding=1, text=['悪魔の子']))
        tags.add(TPE1(encoding=1, text=['ヒグチアイ']))
        tags.save(path, v2_version=3)
        before = path.read_bytes()
        # 临时文件只含标签；由官方 EasyID3 实际解码，替代音频流探测。
        audio = SimpleNamespace(tags=EasyID3(path))
        self.assertEqual(ID3(path)['TIT2'].encoding, 1)
        with patch('backend.audio_metadata.File', return_value=audio) as reader:
            self.assertEqual(read_audio_metadata(path), ('悪魔の子', 'ヒグチアイ'))
            reader.assert_called_once_with(str(path.resolve()), easy=True)
        self.assertEqual(path.read_bytes(), before)

    def test_multiple_artists_keep_every_value(self):
        path = self.make_file('unknown.mp3')
        audio = SimpleNamespace(tags={'title': ['Call your name'], 'artist': ['澤野弘之', 'R!N/Gemie']})
        with patch('backend.audio_metadata.File', return_value=audio):
            self.assertEqual(read_audio_metadata(path), ('Call your name', '澤野弘之、R!N/Gemie'))

    def test_missing_each_field_falls_back_independently(self):
        cases = [({'title': ['标签歌名']}, ('标签歌名', '文件作者')),
                 ({'artist': ['标签作者']}, ('文件歌名', '标签作者')),
                 ({'title': ['  ', None], 'artist': ['']}, ('文件歌名', '文件作者'))]
        for tags, expected in cases:
            with self.subTest(tags=tags):
                _read_cached.cache_clear()
                path = self.make_file('文件歌名 - 文件作者.mp3')
                with patch('backend.audio_metadata.File', return_value=SimpleNamespace(tags=tags)):
                    self.assertEqual(read_audio_metadata(path), expected)

    def test_filename_fallback_supports_original_and_underscore_names(self):
        cases = [('普通歌名 - 普通作者.mp3', ('普通歌名', '普通作者')),
                 ('Call_of_Silence_-_.mp3', ('Call of Silence', '未知艺术家')),
                 ('Call_your_name_-_RNGemie.mp3', ('Call your name', 'RNGemie')),
                 ('独立歌名.mp3', ('独立歌名', '未知艺术家'))]
        for name, expected in cases:
            with self.subTest(filename=name):
                path = self.make_file(name)
                with patch('backend.audio_metadata.File', return_value=None):
                    self.assertEqual(read_audio_metadata(path), expected)

    def test_raw_id3_tags_in_wav_are_supported(self):
        path = self.make_file('fallback.wav')
        tags = ID3()
        tags.add(TIT2(encoding=1, text=['WAV 歌名']))
        tags.add(TPE1(encoding=1, text=['WAV 作者']))
        with patch('backend.audio_metadata.File', return_value=SimpleNamespace(tags=tags)):
            self.assertEqual(read_audio_metadata(path), ('WAV 歌名', 'WAV 作者'))

    def test_corrupt_file_logs_and_keeps_filename_fallback(self):
        path = self.make_file('损坏歌名 - 作者.mp3')
        # 真实 Mutagen 探测损坏临时文件，不修改或使用项目的音乐文件。
        with self.assertLogs('backend.audio_metadata', level='WARNING') as captured:
            self.assertEqual(read_audio_metadata(path), ('损坏歌名', '作者'))
        self.assertIn(str(path.resolve()), captured.output[0])

    def test_mutagen_error_does_not_escape(self):
        path = self.make_file('异常曲目.mp3')
        with patch('backend.audio_metadata.File', side_effect=MutagenError('测试损坏标签')):
            with self.assertLogs('backend.audio_metadata', level='WARNING'):
                self.assertEqual(read_audio_metadata(path), ('异常曲目', '未知艺术家'))

    def test_cache_reuses_reads_and_invalidates_by_file_version(self):
        path = self.make_file('cache.mp3')
        audio = SimpleNamespace(tags={'title': ['旧歌名'], 'artist': ['作者']})
        with patch('backend.audio_metadata.File', return_value=audio) as reader:
            self.assertEqual(read_audio_metadata(path), ('旧歌名', '作者'))
            self.assertEqual(read_audio_metadata(str(path)), ('旧歌名', '作者'))
            self.assertEqual(reader.call_count, 1)
            previous = path.stat()
            audio.tags['title'] = ['时间戳更新']
            os.utime(path, ns=(previous.st_atime_ns, previous.st_mtime_ns + 1_000_000_000))
            self.assertEqual(read_audio_metadata(path), ('时间戳更新', '作者'))
            audio.tags['title'] = ['大小更新']
            path.write_bytes(b'changed file size')
            os.utime(path, ns=(previous.st_atime_ns, previous.st_mtime_ns + 1_000_000_000))
            self.assertEqual(read_audio_metadata(path), ('大小更新', '作者'))
            self.assertEqual(reader.call_count, 3)
        self.assertEqual(_read_cached.cache_info().maxsize, 256)

    def test_missing_file_returns_fallback_with_warning(self):
        path = self.root / 'missing - artist.mp3'
        with self.assertLogs('backend.audio_metadata', level='WARNING'):
            self.assertEqual(read_audio_metadata(path), ('missing', 'artist'))


class AudioCoverTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='blog-audio-cover-tests-')
        self.root = Path(self.temporary.name)
        self.path = self.root / '封面（测试）.mp3'
        self.path.write_bytes(b'temporary audio placeholder')

    def tearDown(self):
        self.temporary.cleanup()

    @staticmethod
    def image_bytes(color: str = 'red', format_name: str = 'PNG') -> bytes:
        buffer = io.BytesIO()
        Image.new('RGB', (4, 4), color).save(buffer, format=format_name)
        return buffer.getvalue()

    def test_apic_prefers_front_cover_and_uses_actual_image_mime(self):
        front, back = self.image_bytes(), self.image_bytes('blue', 'JPEG')
        tags = ID3()
        tags.add(APIC(mime='image/jpeg', type=4, desc='back', data=back))
        # 故意伪造 MIME，必须以图片真实内容为准。
        tags.add(APIC(mime='text/html', type=3, desc='front', data=front))
        with patch('backend.audio_metadata.File', return_value=SimpleNamespace(tags=tags)) as reader:
            self.assertEqual(read_audio_cover(self.path), (front, 'image/png'))
            reader.assert_called_once_with(self.path, easy=False)

    def test_invalid_and_oversize_front_covers_fall_back_to_valid_image(self):
        back = self.image_bytes('blue')
        for invalid in (b'<svg xmlns="http://www.w3.org/2000/svg"></svg>', b'x' * (MAX_COVER_BYTES + 1)):
            with self.subTest(bytes=len(invalid)):
                tags = ID3()
                tags.add(APIC(mime='image/png', type=3, desc='front', data=invalid))
                tags.add(APIC(mime='image/png', type=4, desc='back', data=back))
                with patch('backend.audio_metadata.File', return_value=SimpleNamespace(tags=tags)):
                    self.assertEqual(read_audio_cover(self.path), (back, 'image/png'))

    def test_flac_mp4_and_vorbis_cover_fields(self):
        image = self.image_bytes()
        picture = Picture()
        picture.type, picture.mime, picture.data = 3, 'image/png', image
        encoded = base64.b64encode(picture.write()).decode('ascii')
        cases = [
            SimpleNamespace(tags={}, pictures=[picture]),
            SimpleNamespace(tags={'covr': [MP4Cover(image)]}),
            SimpleNamespace(tags={'metadata_block_picture': [encoded]}),
            SimpleNamespace(tags={'coverart': [base64.b64encode(image).decode('ascii')]}),
        ]
        for audio in cases:
            with self.subTest(tags=tuple(audio.tags)):
                with patch('backend.audio_metadata.File', return_value=audio):
                    self.assertEqual(read_audio_cover(self.path), (image, 'image/png'))

    def test_bad_base64_and_corrupt_vorbis_blocks_do_not_escape(self):
        values = ['not base64!', base64.b64encode(b'invalid picture block').decode('ascii')]
        for value in values:
            with self.subTest(value=value):
                with patch('backend.audio_metadata.File', return_value=SimpleNamespace(tags={'metadata_block_picture': [value]})):
                    self.assertIsNone(read_audio_cover(self.path))

    def test_no_cover_and_unrecognized_audio_return_none(self):
        for audio in (None, SimpleNamespace(tags=None), SimpleNamespace(tags={})):
            with self.subTest(audio=audio):
                with patch('backend.audio_metadata.File', return_value=audio):
                    self.assertIsNone(read_audio_cover(self.path))

    def test_image_pixel_limit_is_applied_before_verification(self):
        image = SimpleNamespace(format='PNG', width=8000, height=6000)
        with patch('backend.audio_metadata.File', return_value=SimpleNamespace(tags={'covr': [b'placeholder']})):
            with patch('backend.audio_metadata.Image.open') as opened:
                opened.return_value.__enter__.return_value = image
                self.assertIsNone(read_audio_cover(self.path))

    def test_cover_read_error_logs_and_returns_none(self):
        with patch('backend.audio_metadata.File', side_effect=MutagenError('测试损坏音频')):
            with self.assertLogs('backend.audio_metadata', level='WARNING') as captured:
                self.assertIsNone(read_audio_cover(self.path))
        self.assertIn(str(self.path), captured.output[0])

    def test_real_wav_apic_is_read_without_writing_or_caching_image(self):
        path = self.root / '内嵌封面.wav'
        with wave.open(str(path), 'wb') as audio:
            audio.setnchannels(1)
            audio.setsampwidth(2)
            audio.setframerate(8000)
            audio.writeframes(b'\x00\x00' * 800)
        metadata = WAVE(path)
        metadata.add_tags()
        cover = self.image_bytes()
        metadata.tags.add(APIC(mime='image/png', type=3, desc='', data=cover))
        metadata.save()
        before = path.read_bytes()
        self.assertEqual(read_audio_cover(path), (cover, 'image/png'))
        self.assertEqual(path.read_bytes(), before)
        metadata.tags.delall('APIC')
        metadata.save()
        self.assertIsNone(read_audio_cover(path))


if __name__ == '__main__':
    unittest.main(verbosity=2)
