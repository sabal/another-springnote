#!/usr/bin/env python3
# coding: utf8
from __future__ import print_function

import json
import os

from springnote import Springnote, SpringnoteException

try:
    raw_input
    input = raw_input
except:
    pass


def makedirs(path, exist_ok=False):
    try:
        os.makedirs(path)
    except OSError:
        pass


class Fetcher:
    def __init__(self):
        openid = input('OpenID (e.g. http://example.myid.net/) : ')
        print('''다음 주소로 가서 API 키를 받으십시오.
Go to following URL and get the user key:
https://api.openmaru.com/delegate_key/springnote?app_id=71fcb7c8'''
            '&openid={}'.format(openid))
        key = input('Key: ')
        print('Connecting...')
        self.api = Springnote(openid, key)

    SAVE_PATH = '_api'

    def fetch(self, path):
        assert '..' not in path
        cache_path = os.path.normpath(self.SAVE_PATH + path)
        if os.access(cache_path, os.F_OK):
            return open(cache_path, 'rb').read()
        makedirs(os.path.split(cache_path)[0], exist_ok=True)
        try:
            data = self.api._fetch('GET', path)
        except SpringnoteException as ex:
            if ex.status in [404]:
                return None
            raise
        open(cache_path, 'wb+').write(data)
        return data


def main():
    bot = Fetcher()
    pages = json.loads(bot.fetch('/pages.json').decode('ascii'))
    n_rev = n_att = 0
    print('{} / {} pages'.format(0, len(pages)))
    for i, entry in enumerate(pages):
        id_ = entry['page']['identifier']
        bot.fetch('/pages/{}.json'.format(id_))
        for resource in ['collaboration', 'comments']:
            bot.fetch('/pages/{}/{}.json'.format(id_, resource))
        data = bot.fetch('/pages/{}/revisions.json'.format(id_))
        if data:
            revisions = json.loads(data.decode('ascii'))
            for k, _ in enumerate(revisions):
                bot.fetch('/pages/{}/revisions/{}.json'.format(
                    id_, _['revision']['identifier']))
            n_rev += len(revisions)
        data = bot.fetch('/pages/{}/attachments.json'.format(id_))
        if data:
            attachments = json.loads(data.decode('ascii'))
            for k, _ in enumerate(attachments):
                bot.fetch('/pages/{}/attachments/{}'.format(id_,
                    _['attachment']['identifier']))
            n_att += len(attachments)
        print('{} / {} pages - {}'.format(
            i + 1, len(pages), entry['page']['title'].encode('utf8')))
    tags = json.loads(bot.fetch('/tags.json').decode('ascii'))
    return
    print('{} / {} tags'.format(0, len(tags)))
    for i, entry in enumerate(tags):
        id_ = entry['tag']['identifier']
        bot.fetch('/tag/{}.json'.format(id_))
        print('{} / {} tags'.format(i + 1, len(tags)))


if __name__ == '__main__':
    main()