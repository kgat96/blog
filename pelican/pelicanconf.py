#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals
from os import getenv

SUTHOR = u'Kage Shen'
SITENAME = u'Kage\'s Blog'
SITEURL = u'http://blog.kfatso.com/'
#SITEURL = '//' + getenv("SITEURL", default='localhost:8000')

PATH = 'content'
TIMEZONE = 'Asia/Hong_Kong'
DEFAULT_LANG = 'en'
THEME = 'gum'


# Feed generation is usually not desired when developing
FEED_ALL_ATOM = 'feeds/all.atom.xml'
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Blogroll
LINKS = (('Pelican', 'http://getpelican.com/'),
         ('Python.org', 'http://python.org/'),)

# Social widget
SOCIAL = ( ('GitHub', 'https://github.com/'),     
           ('FaceBook', 'https://www.facebook.com/'),)

DEFAULT_PAGINATION = 10

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True

################################

#DISPLAY_PAGES_ON_MENU = False
#DISPLAY_CATEGORIES_ON_MENU = False

MENUITEMS = (
    ('Tags', '/functions/tags.html'),
    ('Archives', '/functions/archives.html'), 
)

SITESUBTITLE = 'Stay Hungry, Stay Foolish.'

ARTICLE_URL = 'articles/{date:%Y}/{date:%m}/{date:%d}/{slug}/'
ARTICLE_SAVE_AS = 'articles/{date:%Y}/{date:%m}/{date:%d}/{slug}/index.html'

#PAGE_URL = 'pages/{slug}.html'
#PAGE_SAVE_AS = 'pages/{slug}.html'


#TAGS_URL = 'functions/tags.html'
#TAGS_SAVE_AS = 'functions/tags.html'

ARCHIVES_URL = 'functions/archives.html'
ARCHIVES_SAVE_AS = 'functions/archives.html'

#AUTHORS_URL = 'functions/authors.html'
#AUTHORS_SAVE_AS = 'functions/authors.html'

GITHUB_URL = 'https://github.com/'
FACEBOOK_URL = 'https://www.facebook.com/'

GOOGLE_ANALYTICS = u'UA-60962023-1'
DISQUS_SITENAME = u"kgat96"
#RELATIVE_URLS = False

# plugins
PLUGIN_PATH = 'plugins'
PLUGINS = ['summary','sitemap','neighbors','global_license']








