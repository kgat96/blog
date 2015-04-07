#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals
from os import getenv

AUTHOR = u'Kage Shen'
SITENAME = u'Kage\'s Blog'
SITEURL = u'http://kgat96.github.io/'
#SITEURL = '//' + getenv("SITEURL", default='localhost:8000')

PATH = 'content'

TIMEZONE = 'Asia/Hong_Kong'
DEFAULT_LANG = 'zh'
LOCALE = 'zh_HK.utf8'

GOOGLE_ANALYTICS = u'UA-60962023-1'
DISQUS_SITENAME = u"kgat96"
RELATIVE_URLS = False

#DATE_FORMATS = {
#'zh': ((u'zh_HK', 'utf8'), u'%Y年%m月%d日(週%a)',),
#'zhs': ((u'zh_CN', 'utf8'), u'%Y年%m月%d日(周%a)',),
#}

THEME = 'zurb-F5-basic'

PLUGIN_PATH = u"plugins"

PLUGINS = ["i18n_subsites",
"better_codeblock_line_numbering",
#"disqus_static"
#"plantuml",
#"youku",
#"youtube",
#'tipue_search',
'neighbors',
'series',
#'bootstrapify',
#'twitter_bootstrap_rst_directives',
"render_math",
#'extract_toc',
'sitemap',
'summary']

SITEMAP = {
'format': 'xml',
}

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Blogroll
LINKS = (('Pelican', 'http://getpelican.com/'),
         ('Python.org', 'http://python.org/'),
         ('google', '#'),)

# Social widget
SOCIAL = (('Github', '#'),)

DEFAULT_PAGINATION = 10

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True
