# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2022-12-08 13:11:09
@Author  : Rey
@Contact : reyxbo@163.com
@Explain : Common methods.
"""


from .rbase import warn, exc
from .rcompress import rzip
from .rdata import count, flatten, split, unique, ins, mutual_in
from .rdatabase import REngine
from .rdatetime import RTimeMark, now, time2str, str2time, sleep
from .remail import REmail
from .rfile import read_file, write_file
from .rimage import encode_qrcode, decode_qrcode, compress_image
from .rmultitask import threads
from . import roption
from .rother import digits, randn, get_paths, str2n, n2ch
from .rregular import re_searches, re_subs
from .rrequest import request, download, url_join, url_split, cookie_join, cookie_split, content_type
from .rtext import rprint
from .rwrap import runtime, try_exc