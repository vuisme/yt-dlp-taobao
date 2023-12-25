import re

from yt_dlp.utils import (
    ExtractorError,
    clean_html,
    float_or_none,
    get_element_by_attribute,
    get_element_by_class,
    int_or_none,
    js_to_json,
    traverse_obj,
    url_or_none,
)

from yt_dlp.extractor.amazon import AmazonStoreIE


class AmazonStoreIE_GetThumb(AmazonStoreIE, plugin_name='amz_getimg'):
    _VALID_URL = r'https?://(?:www\.)?amazon\.(?:[a-z]{2,3})(?:\.[a-z]{2})?/(?:[^/]+/)?(?:dp|gp/product)/(?P<id>[^/&#$?]+)'

    _TESTS = [{
        'url': 'https://www.amazon.co.uk/dp/B098XNCHLD/',
        'info_dict': {
            'id': 'B098XNCHLD',
            'title': str,
        },
        'playlist_mincount': 1,
        'playlist': [{
            'info_dict': {
                'id': 'A1F83G8C2ARO7P',
                'ext': 'mp4',
                'title': 'mcdodo usb c cable 100W 5a',
                'thumbnail': r're:^https?://.*\.jpg$',
                'duration': 34,
            },
        }],
        'expected_warnings': ['Unable to extract data'],
    }, {
        'url': 'https://www.amazon.in/Sony-WH-1000XM4-Cancelling-Headphones-Bluetooth/dp/B0863TXGM3',
        'info_dict': {
            'id': 'B0863TXGM3',
            'title': str,
        },
        'playlist_mincount': 4,
        'expected_warnings': ['Unable to extract data'],
    }, {
        'url': 'https://www.amazon.com/dp/B0845NXCXF/',
        'info_dict': {
            'id': 'B0845NXCXF',
            'title': str,
        },
        'playlist-mincount': 1,
        'expected_warnings': ['Unable to extract data'],
    }, {
        'url': 'https://www.amazon.es/Samsung-Smartphone-s-AMOLED-Quad-c%C3%A1mara-espa%C3%B1ola/dp/B08WX337PQ',
        'info_dict': {
            'id': 'B08WX337PQ',
            'title': str,
        },
        'playlist_mincount': 1,
        'expected_warnings': ['Unable to extract data'],
    }]

    def _real_extract(self, url):
        id = self._match_id(url)
        for retry in self.RetryManager():
            webpage = self._download_webpage(url, id)
            try:
                data_json = self._search_json(
                    r'var\s?obj\s?=\s?jQuery\.parseJSON\(\'', webpage, 'data', id,
                    transform_source=js_to_json)
            except ExtractorError as e:
                retry.error = e
        title = data_json.get('title') or ""
        vid = data_json.get('mediaAsin') or ""
        videolst = []
        for video in (data_json.get('videos') or []):
            if video.get('isVideo') and video.get('url'):
                vid = video['marketPlaceID']
                videolst.append({
                    'id': video['marketPlaceID'],
                    'url': video['url'],
                    'title': video.get('title'),
                    'thumbnail': video.get('thumbUrl') or video.get('thumb'),
                    'duration': video.get('durationSeconds'),
                    'height': int_or_none(video.get('videoHeight')),
                    'width': int_or_none(video.get('videoWidth')),
                })
        # print(videolst)
        imagelst = []
        jsonImage = data_json.get('colorImages')
        for i in (jsonImage or {}):
            for colorimg in jsonImage[i]:
                if colorimg.get('hiRes'):
                    # print(colorimg['hiRes'])
                    imagelst.append({
                        'url': colorimg['hiRes'],
                    })
        formats = []
        if not videolst:
            formats.append({
                'url': 'http://bo.vutn.net/no-video.mp4',
                'ext': 'mp4',
                'format_id': 'http-mp4',
            })
        else:
            formats.append({
                'url': videolst[0]['url'],
                'ext': 'mp4',
                'format_id': 'http-mp4',
            })
        # print(imagelst)
        if not formats:
            self.raise_no_formats('No video found for this customer review', expected=True)
        return {
            'id': vid,
            'title': title,
            'thumbnails': imagelst,
            'formats': formats,
        }