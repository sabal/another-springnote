#!/usr/bin/env python3
# coding: utf8
from __future__ import print_function, unicode_literals

import json
import os
import sys
from urllib2 import unquote
from xml.sax.saxutils import escape

from lxml.builder import E
import lxml.etree
import lxml.html


try:
    raw_input
    input = raw_input
except:
    pass

if '.exe' in __file__:  # XXX
    __file__ = sys.argv[0]
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAVE_ROOT = os.path.join(BASE_DIR, '_mediawiki')


def makedirs(path, exist_ok=False):
    try:
        os.makedirs(path)
    except OSError as e:
        if not exist_ok:
            raise
        import errno
        if e.errno not in [errno.EEXIST]:
            raise


def _load(subdomain, path):
    with open(os.path.join(BASE_DIR, '_api', subdomain,
            os.path.normpath(path) + '.json')) as f:
        return json.loads(f.read())


def _save(path, data):
    if isinstance(data, unicode):
        data = data.encode('utf8')
    path = os.path.join(SAVE_ROOT, os.path.normpath(path))
    makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb+') as f:
        f.write(data)


def main():
    if not os.path.exists(os.path.join(BASE_DIR, '_api')):
        print("Springnote backup not found.")
        return
    dirs = os.listdir(os.path.join(BASE_DIR, '_api'))
    if len(dirs) == 0:
        print("Springnote backup not found.")
        return
    elif len(dirs) == 1:
        subdomain = dirs[0]
    else:
        subdomain = None
        while subdomain not in dirs:
            subdomain = input("Choose ID ({}) : ".format(
                ', '.join(sorted(dirs))))

    print("Initializing...")
    makedirs(SAVE_ROOT, exist_ok=True)
    xslt = lxml.etree.XSLT(lxml.etree.parse(open(
        os.path.join(BASE_DIR, 'html2wiki.xsl'))))

    pages = _load(subdomain, 'pages')
    print("Converting XHTML to MediaWiki...")
    output_path = os.path.join(SAVE_ROOT, '{}.xml'.format(subdomain))
    open(output_path, 'w+').write('<mediawiki>\n')
    for i, entry in enumerate(pages):
        id_ = entry['page']['identifier']
        page = _load(subdomain, 'pages/{}'.format(id_))
        xhtml = u'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"
    "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html version="-//W3C//DTD XHTML 1.1//EN"
    xmlns="http://www.w3.org/1999/xhtml" xml:lang="en"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://www.w3.org/1999/xhtml
    http://www.w3.org/MarkUp/SCHEMA/xhtml11.xsd"
    >
<head></head>
<body>{}</body>
</html>'''.format(page['page']['source'])
        xhtml_tree = lxml.html.fromstring(xhtml.encode('utf8'))
        for img in xhtml_tree.xpath('//img'):
            src = img.get('src')
            if not src:
                continue
            if src.startswith('http://eq.springnote.com/tex_image?source='):
                _, _, tex = src.partition(
                    'http://eq.springnote.com/tex_image?source=')
                tex = unquote(tex)
                img.addprevious(E.span('$ {} $'.format(tex)))
        wiki_text = unicode(xslt(xhtml_tree))
        _, _, wiki_text = wiki_text.partition('html2wiki.xsl Wikitext Output')
        wiki_text = wiki_text.strip()
        wiki_text = escape(wiki_text)
        title = page['page']['title']
        with open(output_path, 'a') as fp:
            fp.write('<page>\n')
            fp.write(u'<title>{}</title>\n'.format(
                escape(title)).encode('utf-8'))
            fp.write('<revision>\n')
            fp.write(u'<text>{}</text>\n'.format(wiki_text).encode('utf-8'))
            fp.write('</revision>\n')
            fp.write('</page>\n')
        print(b"{} / {} pages - {}".format(
            i + 1, len(pages), title.encode('utf8')))
    open(output_path, 'a').write('<mediawiki>\n')


if __name__ == '__main__':
    main()
