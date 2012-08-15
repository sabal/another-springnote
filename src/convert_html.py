#!/usr/bin/env python3
# coding: utf8
from __future__ import print_function

import json
import os
import re
import shutil

import lxml.html

try:
    raw_input
    input = raw_input
except:
    pass

if '.exe' in __file__:  # XXX
    import sys
    __file__ = sys.argv[0]
NTFS_NG = '\0/\\:*?"<>|'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAVE_ROOT = os.path.join(BASE_DIR, '_html')


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
            subdomain = input("Choose ID ({}) : ".format(', '.join(dirs)))
    shutil.copy2(
        os.path.join(BASE_DIR, 'sabal.css'),
        os.path.join(SAVE_ROOT, 'pages'))
    pages = _load(subdomain, 'pages')

    print("Copying attachments...")
    attachment_file_name = {}
    for i, entry in enumerate(pages):
        id_ = str(entry['page']['identifier'])
        attachments = _load(subdomain, 'pages/{}/attachments'.format(id_))
        for entry in attachments:
            att_id = str(entry['attachment']['identifier'])
            file_name = entry['attachment']['title']
            for ch in NTFS_NG:
                file_name = file_name.replace(ch, '')
            if not file_name:
                file_name = 'None'
            attachment_file_name[(id_, att_id)] = file_name
            source_path = os.path.join(BASE_DIR, '_api', subdomain,
                'pages', str(id_), 'attachments', str(att_id))
            dest_path = os.path.join(SAVE_ROOT, 'pages',
                '{}.attachments'.format(id_), str(att_id), file_name)
            makedirs(os.path.dirname(dest_path), exist_ok=True)
            shutil.copy(source_path, dest_path)

    print("Converting XHTML...")
    for i, entry in enumerate(pages):
        id_ = entry['page']['identifier']
        page = _load(subdomain, 'pages/{}'.format(id_))
        title = page['page']['title']
        xhtml = b'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"
    "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html version="-//W3C//DTD XHTML 1.1//EN"
    xmlns="http://www.w3.org/1999/xhtml" xml:lang="en"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://www.w3.org/1999/xhtml
    http://www.w3.org/MarkUp/SCHEMA/xhtml11.xsd"
    >
  <head>
    <meta http-equiv="Content-Type" content="text/html;charset=UTF-8" />
    <title>{title}</title>
    <link href="sabal.css" rel="stylesheet" media="screen" type="text/css">
  </head>
  <body>
    {body}
  </body>
</html>
'''.format(
            title=title.encode('utf8'),
            body=page['page']['source'].encode('utf8'))
        tree = lxml.html.fromstring(xhtml)
        for a in tree.cssselect('a.wiki'):
            href = a.get('href', '')
            m = re.match('^/pages/(\d+)$', href)
            if not m:
                continue
            a.set('href', '{}.xhtml'.format(m.group(1)))
        for a in tree.cssselect('img'):
            src = a.get('src', '')
            m = re.match((
                r'^(http://{}\.springnote\.com)?'
                r'/pages/(?P<id>\d+)/attachments/(?P<att_id>\d+)$').format(
                    subdomain),
                src)
            if not m:
                continue
            if (m.group('id'), m.group('att_id')) not in attachment_file_name:
                continue
            src = unicode('{}.attachments/{}/{}').format(
                m.group('id'), m.group('att_id'),
                attachment_file_name[(m.group('id'), m.group('att_id'))])
            a.set('src', src)
        _save('pages/{}.xhtml'.format(id_),
            lxml.html.tostring(tree, method='xml', encoding='utf8'))

        print("{} / {} pages - {}".format(
            i + 1, len(pages), title.encode('utf8')))
    print("Converted contents at: {}".format(SAVE_ROOT))


if __name__ == '__main__':
    main()