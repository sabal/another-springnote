#!/usr/bin/env python3
from __future__ import print_function

import calendar
import gzip
import os
import re
import time

import json
# import phpserialize

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOKUWIKI_ROOT = os.path.join(BASE_DIR, 'dokuwiki')


def _load(path):
    with open(os.path.join(BASE_DIR, '_api',
            os.path.normpath(path) + '.json')) as f:
        return json.loads(f.read())


def _save(path, data):
    with open(os.path.join(DOKUWIKI_ROOT, 'data',
            os.path.normpath(path)), 'wb+') as f:
        f.write(data.encode('utf8'))


def main():
    pages = _load('pages')
    print('0 / {} pages'.format(len(pages)), end='')
    for i, entry in enumerate(pages):
        id_ = entry['page']['identifier']
        page = _load('pages/{}'.format(id_))
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
        _save('pages/{}.xhtml'.format(id_), xhtml)
        # revision
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
        print('\r{} / {} pages'.format(i + 1, len(pages)), end='')
    print('')


main()
