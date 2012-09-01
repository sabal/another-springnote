#!/usr/bin/env python3
# coding: utf8
from __future__ import print_function, unicode_literals

import datetime
import os
import sys
from urllib2 import unquote
from xml.sax.saxutils import escape

from lxml.builder import E
import lxml.etree
import lxml.html

import util

try:
    raw_input
    input = raw_input
except:
    pass

if '.exe' in __file__:  # XXX
    __file__ = sys.argv[0]
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAVE_ROOT = os.path.join(BASE_DIR, '_mediawiki')
MEDIAWIKI_NG = {
    '+': '＋',
    '|': '｜',
    '{': '｛',
    '}': '｝',
}
XSLT = lxml.etree.XSLT(lxml.etree.parse(open(
        os.path.join(BASE_DIR, 'html2wiki.xsl'))))



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
    util.makedirs(SAVE_ROOT, exist_ok=True)

    pages = util.load_resource(subdomain, 'pages')
    print("Converting XHTML to MediaWiki...")
    output_path = os.path.join(SAVE_ROOT, '{}.xml'.format(subdomain))
    output_fp = open(output_path, 'w+')
    output_fp.write('<mediawiki>\n')
    id2title = {str(_['page']['identifier']): _['page']['title'] for _ in pages}
    n = 0
    titles = set()
    for entry in pages:
        id_ = entry['page']['identifier']
        if not util.is_public(subdomain, id_):
            continue

        page = util.load_resource(subdomain, 'pages/{}'.format(id_))
        title = page['page']['title']
        new_title = title
        for k, v in MEDIAWIKI_NG.items():
            new_title = new_title.replace(k, v)
        j = 1
        new_title_ = new_title
        while new_title_ in titles:
            j += 1
            new_title_ = new_title + ' ({})'.format(j)
        new_title = new_title_
        titles.add(new_title)
        revisions_data = util.load_resource(subdomain,
                'pages/{}/revisions'.format(id_))
        if revisions_data:
            revisions = sorted(revisions_data,
                    key=lambda _: _['revision']['date_created'])
        else:
            revisions = []
        output_fp.write('<page>\n')
        output_fp.write(u'<title>{}</title>\n'.format(
            escape(new_title)).encode('utf-8'))
        wiki_text = ''
        for revision in revisions:
            timestamp = util.parse_timestamp(
                        revision['revision']['date_created'])
            timestamp = datetime.datetime.utcfromtimestamp(timestamp).strftime(
                    '%Y-%m-%dT%H:%M:%SZ')
            revision_data = util.load_resource(subdomain,
                'pages/{}/revisions/{}'.format(
                    id_, revision['revision']['identifier']))
            source = revision_data['revision']['source']
            wiki_text = (sabal2mediawiki(source, id2title) if source
                    else wiki_text)  # previous revision
            output_fp.write('<revision>\n')
            output_fp.write('<timestamp>{}</timestamp>\n'.format(timestamp))
            if revision['revision'].get('creator'):
                output_fp.write('<contributor><username>{}'
                    '</username></contributor>\n'.format(
                        escape(revision['revision']['creator'])))
            if revision['revision'].get('description'):
                output_fp.write(u'<comment>{}</comment>\n'.format(
                    escape(revision['revision']['description'])).encode('utf-8'))
            output_fp.write(u'<text>{}</text>'
                u'\n'.format(escape(wiki_text)).encode('utf-8'))
            output_fp.write('</revision>\n')
        output_fp.write('</page>\n')
        n += 1
        print(b"{} / {} pages - {}".format(
            n, len(pages), title.encode('utf8')))
    print("Not processing {} private pages".format(len(pages) - n))
    output_fp.write('</mediawiki>\n')
    print("Converted XML at: {}".format(output_path))


def sabal2mediawiki(source, id2title):
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
</html>'''.format(source)
    xhtml_tree = lxml.html.fromstring(xhtml.encode('utf8'))
    for li in xhtml_tree.xpath('//li'):
        for p in li.findall('p'):
            p.addnext(E.br())
            p.drop_tag()
    for a in xhtml_tree.xpath('//a'):
        href = a.get('href')
        if not href:
            continue
        if href.startswith('/pages/'):
            _, _, target_id = href.partition('/pages/')
            target_title = id2title.get(target_id, target_id)
            target_href = u'/wiki/{}'.format(target_title)
            a.set('href', target_href)
    for img in xhtml_tree.xpath('//img'):
        src = img.get('src')
        if not src:
            continue
        tex = None
        if src.startswith('http://bomber0.byus.net/mimetex/mimetex.cgi?'):
            _, _, tex = src.partition(
                'http://bomber0.byus.net/mimetex/mimetex.cgi?')
        if src.startswith('http://eq.springnote.com/tex_image?source='):
            _, _, tex = src.partition(
                'http://eq.springnote.com/tex_image?source=')
        if tex:
            tex = unquote(tex)
            img.addprevious(E.span('<math>{}</math>'.format(tex)))
            img.drop_tag()
            continue
        if img.get('class') == 'attachment':
            img.addprevious(E.a(img.get('title', ''), href=src or 'attachments/error'))
            continue
    wiki_text = unicode(XSLT(xhtml_tree))
    _, _, wiki_text = wiki_text.partition('html2wiki.xsl Wikitext Output')
    return wiki_text.strip()


if __name__ == '__main__':
    main()
