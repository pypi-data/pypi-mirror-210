import os
import mimetypes

from .constant import TYPE


def get_ext(p: str) -> str:
    return os.path.splitext(p)[1][1:]


def guess_mime(p: str) -> str:
    a, b = mimetypes.guess_type(p, False)
    if b in 'gzip bzip2 xz'.split():
        return TYPE.ARCHIVE
    if a is None:
        return TYPE.UNKNOWN
    if a.startswith('video/'):
        return TYPE.VIDEO
    if a.startswith('audio/'):
        return TYPE.AUDIO
    if a.startswith('image/'):
        if 'image/gif' in a:
            return TYPE.GIF
        if 'image/svg' in a:
            return TYPE.SVG
        return TYPE.IMAGE
    if a.startswith('text/'):
        return TYPE.TEXT

    if a.startswith('application/'):
        if a.startswith('application/x-'):
            for i in 'tar zip compress'.split():
                if i in a:
                    return TYPE.ARCHIVE
        for i in 'vnd.ms msword office pdf'.split():
            if i in a:
                return TYPE.OFFICE

    return TYPE.UNKNOWN


ext_type = {
    TYPE.UNKNOWN: '',
    TYPE.ARCHIVE: 'iso rar 7z s7z dmg sz zst qflac blv',
    # zip tar gz tgz bz2 tbz2 xz txz z
    TYPE.VIDEO: 'flv ts rmvb f4v f4a',
    # webm mkv avi mts m2ts mov wmv mp4 m4v mpg mpeg mpe 3gp
    # TYPE.AUDIO: 'aac flac m4a mp3 wav ogg',
    # TYPE.IMAGE: 'jpg jpeg png webp tif tiff bmp',
    # TYPE.GIF: 'gif',
    # TYPE.SVG: 'svg',
    # TYPE.OFFICE: 'doc docx ppt pptx xls xlsx pdf xps',
    TYPE.EXECUTABLE: 'com exe cmd vbe jse wsf msc jar msi',
    TYPE.TEXT: 'txt text in out log csv',
    TYPE.CONFIG: 'conf config xml toml json',
    TYPE.CODE: 'md tex c cpp h hpp cc java pyi py sh ps1 bat cs go lua pas php r rb swift vb vbs html js css'
}

ext_re = dict()
for i in ext_type:
    for j in ext_type[i].split(' '):
        assert j not in ext_re
        ext_re[j] = i


def guess_ext(p: str) -> str:
    return ext_re.get(get_ext(p), TYPE.UNKNOWN)
