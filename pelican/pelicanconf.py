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

#THEME = 'zurb-F5-basic'
THEME = 'blue-penguin'

PLUGIN_PATH = u"plugins"

PLUGINS = [
# "i18n_subsites",
"better_codeblock_line_numbering",
# 'neighbors',
# 'series',
"render_math",
'sitemap',
# 'summary'
]

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

PAGINATION_PATTERN = True
DEFAULT_PAGINATION = 10

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True

# all the following settings are *optional*

# all defaults to True.
DISPLAY_HEADER = True
DISPLAY_FOOTER = True
DISPLAY_HOME   = True
DISPLAY_MENU   = True

# provided as examples, they make ‘clean’ urls. used by MENU_INTERNAL_PAGES.
TAGS_URL           = 'tags'
TAGS_SAVE_AS       = 'tags/index.html'
AUTHORS_URL        = 'authors'
AUTHORS_SAVE_AS    = 'authors/index.html'
CATEGORIES_URL     = 'categories'
CATEGORIES_SAVE_AS = 'categories/index.html'
ARCHIVES_URL       = 'archives'
ARCHIVES_SAVE_AS   = 'archives/index.html'

# use those if you want pelican standard pages to appear in your menu
MENU_INTERNAL_PAGES = (
#    ('Tags', TAGS_URL, TAGS_SAVE_AS),
#    ('Authors', AUTHORS_URL, AUTHORS_SAVE_AS),
#    ('Categories', CATEGORIES_URL, CATEGORIES_SAVE_AS),
    ('Archives', ARCHIVES_URL, ARCHIVES_SAVE_AS),
)

# additional menu items
MENUITEMS = (
#    ('GitHub', 'https://github.com/'),
#    ('Linux Kernel', 'https://www.kernel.org/'),
)



