# coding: utf-8
import json

from yt_dlp.utils import (
    # int_or_none,
    # js_to_json,
    # mimetype2ext,
    ExtractorError,
    remove_end,
)

from yt_dlp.extractor.ebay import EbayIE


class EbayIE_Thumb(EbayIE, plugin_name='ebay_img'):
    IE_NAME = 'ebay:product'
    _VALID_URL = r'https?://(?:www\.)?ebay\.(?:[a-z]{2,3})(?:\.[a-z]{2})?/(?:itm)(?:[/\S])*/(?P<id>[0-9]{9,12})'
    _TESTS = [{
        'url': 'https://www.ebay.com/itm/adidas-Originals-Ultraboost-DNA-XXII-Shoes-Men-039-s-/155249878436?&_trksid=p2056016.m2516.l5255',
        'info_dict': {
            'id': '155249878436',
            'ext': 'mp4',
            'title': 'Video title goes here',
            'thumbnail': r're:^https?://.*\.jpg$',
            # TODO more properties, either as:
            # * A value
            # * MD5 checksum; start the string with md5:
            # * A regular expression; start the string with re:
            # * Any Python type (for example int or float)
        }
    }]

    def _real_extract(self, eurl):
        video_id = self._match_id(eurl)
        webpage, urlh = self._download_webpage_handle(eurl, video_id)
        visitor_url = urlh.url
        if 'login.jhtml' in visitor_url:
            raise ExtractorError(
                'Lỗi đăng nhập Taobao - Cookies Error - Vui lòng báo lỗi cho hỗ trợ @cpanel10x',
                expected=True)
        # initial_state = self._search_json(r'\[\[\"PICTURE0\-0\"\,0\,\{\"model\"\:', webpage, 'initial state', pid)
        # print(initial_state)
        # print(type(initial_state))
        thumb = []
        videoURL = None

        video_json = self._search_json(r'"video":', webpage, 'video json', video_id)
        formats = []
        for key, url in video_json['playlistMap'].items():
            if key == 'HLS':
                formats.extend(self._extract_m3u8_formats(url, video_id, fatal=False))
            elif key == 'DASH':
                formats.extend(self._extract_mpd_formats(url, video_id, fatal=False))
            else:
                self.report_warning(f'Unsupported format {key}', video_id)

        # newjson = json.loads(json.dumps(initial_state))
        # for i in range(len(newjson['mediaList'])):
        #     for key, value in newjson['mediaList'][i].items():
        #         if key in "video":
        #             videoURL = value["playlistMap"]["HLS"]
        #         if key in "image":
        #             thumb.append({
        #                 'url': value["originalImg"]["URL"].replace("l500", "l2000"),
        #             })
        # if not pid:
        #     raise ExtractorError(
        #         'Không thể lấy video/ảnh, vui lòng kiểm tra lại liên kết hoặc liên hệ hỗ trợ',
        #         expected=True)
        # title = self._search_regex(r'<title>([^<]+)<', webpage, 'title')
        if video_id is None:
            return {
                # I have no idea what these params mean but it at least seems to work
                # 'url': "http://bo.vutn.net/no-video.mp4",
                # 'id': pid,
                # 'title': title,
                # 'thumbnails': thumb,
                'id': video_id,
                'title': remove_end(self._html_extract_title(webpage), ' | eBay'),
                'formats': formats
            }
        else:
            return {
            'id': video_id,
            'title': remove_end(self._html_extract_title(webpage), ' | eBay'),
            'formats': formats
            }
