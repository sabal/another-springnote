#!/usr/bin/env python3
# coding: utf8
from __future__ import print_function

import gzip
import json
import os

import lxml
from lxml.builder import E
# import phpserialize

import util

try:
    unicode
except NameError:
    unicode = str

try:
    raw_input
    input = raw_input
except:
    pass


def makedirs(path, exist_ok=False):
    try:
        os.makedirs(path)
    except OSError as e:
        if not exist_ok:
            raise
        import errno
        if e.errno not in [errno.EEXIST]:
            raise


if '.exe' in __file__:  # XXX
    import sys
    __file__ = sys.argv[0]
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOKUWIKI_ROOT = os.path.join(BASE_DIR, '_dokuwiki')


def _load(subdomain, path):
    path = os.path.join(BASE_DIR, '_api', subdomain,
            os.path.normpath(path) + '.json')
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.loads(f.read())


def _save(subdomain, path, data):
    if isinstance(data, unicode):
        data = data.encode('utf8')
    with open(os.path.join(DOKUWIKI_ROOT, subdomain, 'data',
            os.path.normpath(path)), 'wb+') as f:
        f.write(data)


def main():
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
    makedirs(os.path.join(DOKUWIKI_ROOT, subdomain, 'data', 'attic'), exist_ok=True)
    makedirs(os.path.join(DOKUWIKI_ROOT, subdomain, 'data', 'meta'), exist_ok=True)
    makedirs(os.path.join(DOKUWIKI_ROOT, subdomain, 'data', 'pages'), exist_ok=True)
    pages = _load(subdomain, 'pages')
    tree = E.pages()
    node_by_id = {}
    dangling_nodes = {}
#    pages = {_['page']['identifier']: _['page'] for _ in pages}  # No need yet
    print('0 / {} pages'.format(len(pages)))
    for i, entry in enumerate(pages):
        id_ = entry['page']['identifier']
        page = _load(subdomain, 'pages/{}'.format(id_))

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
    <title>{title}</title>
  </head>
  <body>
    {body}
  </body>
</html>
'''.format(
            title=page['page']['title'].encode('utf8'),
            body=page['page']['source'].encode('utf8'))
        # TODO: save private pages in a different path
        _save(subdomain, 'pages/{}.xhtml'.format(id_), xhtml)
        # revisions
        revisions_data = _load(subdomain, 'pages/{}/revisions'.format(id_))
        if revisions_data:
            revisions = sorted(revisions_data,
                    key=lambda _: _['revision']['date_created'])
            data = []
            for k, revision in enumerate(revisions):
                description = revision['revision']['description']
                revision = _load(subdomain, 'pages/{}/revisions/{}'.format(
                    id_, revision['revision']['identifier']))
                timestamp = util.parse_timestamp(
                        revision['revision']['date_created'])
                data.append('\t'.join([
                    str(int(timestamp)),
                    '127.0.0.1',
                    'E' if k else 'C',  # for 'edit' and 'create' respectively
                    str(id_),
                    revision['revision']['creator'] or '',
                    description]))
                source = revision['revision']['source'] or ''
                path = os.path.join(DOKUWIKI_ROOT, subdomain, 'data', 'attic',
                        '{}.{}.xhtml.gz'.format(id_, timestamp))
                with gzip.open(path, 'wb+') as f:
                    f.write(source.encode('utf8'))
            _save(subdomain, 'meta/{}.changes'.format(id_), '\n'.join(data))

        # TODO: attachments
        print(b'{} / {} pages'.format(i + 1, len(pages)))

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
    new_tree = E.pages()
    for node in list(tree.getiterator()):
        if node.tag != 'page':
            continue
        new_tree.append(node)
    _save(subdomain, 'meta/_tree.xml', lxml.etree.tostring(new_tree,
        pretty_print=True, encoding='utf8'))
    # tree with public pages only
    for node in list(new_tree.getiterator()):
        if node.tag in ['pages']:
            continue
        id_ = node.get('id')
        if id_ in ['lost_and_found']:
            continue
        collaboration = _load(subdomain,
            'pages/{}/collaboration'.format(int(id_)))
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
    _save(subdomain, 'pages/_tree.xml', lxml.etree.tostring(new_tree,
        pretty_print=True, encoding='utf8'))


if __name__ == '__main__':
    main()
