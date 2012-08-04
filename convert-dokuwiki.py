#!/usr/bin/env python3
from __future__ import print_function

import calendar
import gzip
import json
import os
import re
import time

import lxml
from lxml.builder import E
# import phpserialize

try:
    unicode
except NameError:
    unicode = str

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOKUWIKI_ROOT = os.path.join(BASE_DIR, 'dokuwiki')


def _load(path):
    with open(os.path.join(BASE_DIR, '_api',
            os.path.normpath(path) + '.json')) as f:
        return json.loads(f.read())


def _save(path, data):
    if isinstance(data, unicode):
        data = data.encode('utf8')
    with open(os.path.join(DOKUWIKI_ROOT, 'data',
            os.path.normpath(path)), 'wb+') as f:
        f.write(data)


def main():
    pages = _load('pages')
    tree = E.pages()
    node_by_id = {}
    dangling_nodes = {}
#    pages = {_['page']['identifier']: _['page'] for _ in pages}  # No need yet
    print('0 / {} pages'.format(len(pages)), end='')
    for i, entry in enumerate(pages):
        id_ = entry['page']['identifier']
        page = _load('pages/{}'.format(id_))

        # tree
        if id_ not in node_by_id:
            node = E.page(id=str(id_))
            node_by_id[id_] = node
        elif id_ in dangling_nodes:
            node = node_by_id[id_]
            del dangling_nodes[id_]
        else:
            raise ValueError('Multiple pages with a same ID: {}'.format(id_))
        node.set('title', entry['page']['title'])
        parent_id = entry['page'].get('relation_is_part_of', None)
        if not parent_id:
            # the root
            tree.append(node)
        elif parent_id in node_by_id:
            node_by_id[parent_id].append(node)
        else:
            assert parent_id not in dangling_nodes
            parent = E.page(node, id=str(parent_id))
            node_by_id[parent_id] = dangling_nodes[parent_id] = parent

        # content
        xhtml = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"
    "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html version="-//W3C//DTD XHTML 1.1//EN"
    xmlns="http://www.w3.org/1999/xhtml" xml:lang="en"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://www.w3.org/1999/xhtml
    http://www.w3.org/MarkUp/SCHEMA/xhtml11.xsd"
    >
  <head>
    <title>{title}</title>
  </head>
  <body>
    {body}
  </body>
</html>
'''.format(
            title=page['page']['title'],
            body=page['page']['source'])
        # TODO: save private pages in a different path
        _save('pages/{}.xhtml'.format(id_), xhtml)
        # revisions
        revisions = sorted(_load('pages/{}/revisions'.format(id_)),
                key=lambda _:_['revision']['date_created'])
        data = []
        for k, revision in enumerate(revisions):
            description = revision['revision']['description']
            revision = _load('pages/{}/revisions/{}'.format(
                id_, revision['revision']['identifier']))
            m = re.match(r'^(?P<parsable>\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}) '
                r'(?P<tz_sign>[-+])(?P<tz_hour>\d{2})(?P<tz_minute>\d{2})$',
                revision['revision']['date_created'])
            # NOTE: strptime cannot parse timezone
            timestamp = calendar.timegm(time.strptime(m.group('parsable'),
                '%Y/%m/%d %H:%M:%S'))
            delta = (int(m.group('tz_hour')) * 3600 +
                    int(m.group('tz_minute')) * 60)
            if m.group('tz_sign') == '-':
                delta = -delta
            timestamp += delta
            data.append('\t'.join([
                str(int(timestamp)),
                '127.0.0.1',
                'E' if k else 'C',  # for 'edit' and 'create' respectively
                str(id_),
                revision['revision']['creator'] or '',
                description]))
            source = revision['revision']['source'] or ''
            with gzip.open(os.path.join(DOKUWIKI_ROOT, 'data', 'attic',
                    '{}.{}.xhtml.gz'.format(id_, timestamp)), 'wb+') as f:
                f.write(source.encode('utf8'))
        _save('meta/{}.changes'.format(id_), '\n'.join(data))

        # TODO: attachments
        print('\r{} / {} pages'.format(i + 1, len(pages)), end='')

    print('')
    print('Saving tree structures...')
    lost_and_found = E.page(id='lost_and_found', title='Lost and Found')
    if dangling_nodes:
        for id_, node in dangling_nodes.items():
            lost_and_found.append(node)
        tree.append(lost_and_found)
    # NOTE: The tree is sorted by title by default; maybe we need to
    #       double-check it
    for node in list(tree.getiterator()):
        if node.tag != 'page':
            continue
        path = []
        parent = node.getparent()
        while parent.tag == 'page':
            path.insert(0, parent.get('id'))
            parent = parent.getparent()
        node.set('path', ':'.join(path))
    _save('meta/_tree.xml', lxml.etree.tostring(tree,
        pretty_print=True, encoding='utf8'))
    # tree with public pages only
    for node in list(tree.getiterator()):
        if node.tag in ['pages']:
            continue
        id_ = node.get('id')
        if id_ in ['lost_and_found']:
            continue
        collaboration = _load('pages/{}/collaboration'.format(int(id_)))
        # The page is public when any of the following is true:
        # - collaboration.json is an empty list
        # - There exists {"access_rights": "reader",
        #                 "rights_holder": "everybody", ...}
        is_public = not collaboration or any(
            _['collaboration']['access_rights'] == 'reader' and
            _['collaboration']['rights_holder'] == 'everybody'
            for _ in collaboration)
        if not is_public:
            for child in node:
                node.remove(child)
                lost_and_found.append(child)
            node.getparent().remove(node)
    # TODO: Sort by title?
    _save('pages/_tree.xml', lxml.etree.tostring(tree,
        pretty_print=True, encoding='utf8'))


main()
