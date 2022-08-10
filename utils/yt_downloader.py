# -*- coding:utf-8 -*-
import os
import yt_dlp
from loader import db
from requests import get
from PIL import Image

CATEGORIES = {
    'intro': 'intermission / intro animation',
    'outro': 'endcards / credits',
    'selfpromo': 'unpaid / self promotion',
    'preview': 'preview / recap',
    'interaction': 'interaction reminder',
    'music_offtopic': 'mussic off-topic'
}

# Suppress noise about console usage from errors
yt_dlp.utils.bug_reports_message = lambda: ''


def extract_info(url: str, u_vquality, u_aquality, segmentsToMark, segmentsToDelete):
    with yt_dlp.YoutubeDL() as ydl:
        info = ydl.extract_info(url, download=False)

    # formats are already sorted worst to best
    pos = None
    formats = info.get('formats')[::-1]
    list_of_formats = []
    invalid_combinations = []
    u_audio = None
    for num, v_format in enumerate(formats):
        filesize = v_format.get('filesize')
        format_id = v_format.get('format_id')

        if filesize is not None:
            if filesize >= 2147483648:
                formats.pop(num)

        if filesize is not None:
            list_of_formats.append((filesize, format_id))
            for v_format in list_of_formats:
                if filesize + v_format[0] >= 2147483648:
                    invalid_combinations.append((format_id, v_format[1]))
                    invalid_combinations.append((v_format[1], format_id))

        # format_id = v_format.get('format_id')
        # fps = v_format.get('fps')
        # height = v_format.get('height')
        # width = v_format.get('width')
        # format_note = v_format.get('format_note')
        # quality = v_format.get('quality')
        # ext = v_format.get('ext')
        # v_codec = v_format.get('vcodec')
        # acodec = v_format.get('acodec')
        #
        # if height is None or width is None or fps is None:
        #     print(f'{filesize=}\n{format_id=}\n{format_note=}\n{quality=}\n{ext=}\n{acodec=}\n{v_codec=}\n')
        # else:
        #     print(f'{filesize=}\n{format_id=}\n{fps=}\n{height=}\n{width=}'
        #           f'\n{format_note=}\n{quality=}\n{ext=}\n{acodec=}\n')
    start_over = True
    while True:
        if start_over:
            start_over = False

            match u_vquality:
                case 'best' | 'no video':
                    u_video = next(f for f in formats
                                   if f['vcodec'] != 'none' and f['acodec'] and f['ext'] == 'mp4')
                case 'worst':
                    u_video = next(f for f in formats[::-1]
                                   if f['vcodec'] != 'none' and f['acodec'] and f['ext'] == 'mp4')
                case _:
                    qualities = ('4320p', '4320p60', '2160p', '2160p60', '1080p', '1080p60',
                                 '720p', '720p60', '360p', '240p', '144p')
                    if pos is None:
                        pos = qualities.index(u_vquality)
                    else:
                        pos += 1
                    try:
                        u_video = next(f for f in formats
                                       if f['format_note'] == u_vquality and f['ext'] == 'mp4')
                    except:
                        found = False
                        for i in qualities[pos:]:
                            for v_format in formats:
                                if i == v_format['format_note']:
                                    u_video = next(f for f in formats
                                                   if f['format_note'] == i and f['ext'] == 'mp4')
                                    found = True
                                    break
                                if found:
                                    break
            if u_vquality != 'no video':
                audio_ext = {'mp4': 'm4a', 'webm': 'webm'}[u_video['ext']]
            else:
                audio_ext = 'm4a'

            match u_aquality:
                case 'best' | 'no audio':
                    u_audio = next(f for f in formats if (
                            f['acodec'] != 'none' and f['vcodec'] == 'none' and f['ext'] == audio_ext))
                case 'worst':
                    u_audio = next(f for f in formats[::-1] if (
                            f['acodec'] != 'none' and f['vcodec'] == 'none' and f['ext'] == audio_ext))
                case _:
                    u_audio = next(f for f in formats if (
                            f['format_note'] == u_aquality))

            if (str(u_video.get('format_id')), str(u_audio.get('format_id'))) in invalid_combinations:
                start_over = True
                continue
        else:
            break

    if u_vquality == 'no video':
        requested_formats, ext, protocol, preferedformat = (u_audio,  # requested_formats
                                                            u_audio['ext'],  # ext
                                                            f'{u_video["protocol"]}+{u_audio["protocol"]}',  # protocol
                                                            'mp3')  # preferedformat
    elif u_aquality == 'no audio':
        requested_formats, ext, protocol, preferedformat = (u_video,  # requested_formats
                                                            u_video['ext'],  # ext
                                                            f'{u_video["protocol"]}',  # protocol
                                                            'mp4')  # preferedformat
    else:
        requested_formats, ext, protocol, preferedformat = ([u_video, u_audio],  # requested_formats
                                                            u_video['ext'],  # ext
                                                            f'{u_video["protocol"]}+{u_audio["protocol"]}',  # protocol
                                                            'mp4')
    return {
        'format': f'{u_video["format_id"]}+{u_audio["format_id"]}',
        'ext': ext,
        'requested_formats': [requested_formats],
        'protocol': f'{u_video["protocol"]}+{u_audio["protocol"]}',
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,

        'key': {'EmbedThumbnail': True},
        'postprocessors': [
            {'key': 'SponsorBlock',
             'categories':
                 segmentsToMark
             },
            {'key': 'ModifyChapters', 'remove_sponsor_segments':
                {segmentsToDelete}},
            {'key': 'FFmpegMetadata', 'add_chapters': True},
            {'key': 'FFmpegVideoConvertor', 'preferedformat': preferedformat}
        ]
    }


def download_video(url, id):
    settings = db.select_user(id=id)
    for key, vallue in CATEGORIES.items():
        segmentsToMark = settings[4].replace(vallue, key).split(', ')
        segmentsToDelete = settings[5].replace(vallue, key).split(', ')
    segmentsToMark += segmentsToDelete
    segmentsToMark = set(segmentsToMark)
    segmentsToDelete = ', '.join(segmentsToDelete)
    res = settings[2].split('Quality: ')[-1].replace('"', '')
    audio_q = settings[3].split('Quality: ')[-1].replace('"', '')
    ytdl_opts = extract_info(url, res, audio_q, segmentsToMark, segmentsToDelete)

    with yt_dlp.YoutubeDL(ytdl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)

    ext = info_dict.get('requested_downloads')[0].get('_filename').split('.')[-1]

    try:
        filename = f"{info_dict.get('requested_downloads')[0].get('_filename').rsplit(' ', 1)[0]}.{ext}"
        os.rename(info_dict.get('requested_downloads')[0].get('_filename'), filename)
    except FileNotFoundError:
        try:
            ext = 'mp3'
            filename = f"{info_dict.get('requested_downloads')[0].get('_filename').rsplit(' ', 1)[0]}.{ext}"
            os.rename(f"{info_dict.get('requested_downloads')[0].get('_filename').rsplit('.', 1)[0]}.{ext}", filename)
        except FileNotFoundError:
            ext = 'mp4'
            filename = f"{info_dict.get('requested_downloads')[0].get('_filename').rsplit(' ', 1)[0]}.{ext}"
            os.rename(f"{info_dict.get('requested_downloads')[0].get('_filename').rsplit('.', 1)[0]}.{ext}", filename)
        except FileExistsError:
            pass
    except FileExistsError:
        pass

    if os.stat(filename).st_size > 2147483648:
        raise 'FileIsTooLarge'

    thumbnail_url = info_dict.get('thumbnails')[-1].get('url')
    thumbnail_filename = 'C:\\Users\\Olyx\\Desktop\\python\\projects\\tbot\\' + thumbnail_url.split('/')[-2] + '.png'
    with open(thumbnail_filename, 'wb') as file:
        file.write(get(thumbnail_url).content)
    image = Image.open(thumbnail_filename)
    image.thumbnail((1280, 720))
    image.save(thumbnail_filename)

    return filename, thumbnail_filename, ext
