#!/usr/bin/env python3
# coding: utf8
from __future__ import print_function

import json
import lxml.html
import os
import re
try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen

from springnote import Springnote, SpringnoteException

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
SAVE_PATH = os.path.join(BASE_DIR, '_api')


class Fetcher:
    def __init__(self):
        openid = input("Your OpenID (e.g. http://example.myid.net/) : ")
        print("""다음 주소로 가서 API 키를 받으십시오.
Go to following URL and get the user key:
https://api.openmaru.com/delegate_key/springnote?app_id=71fcb7c8"""
            '&openid={}'.format(openid))
        key = input("Key: ")
        print("질문 하나만 더 받으면 됩니다. 접속될 때까지 채널 고정!")
        print("Connecting. Please wait...")
        self.api = Springnote(openid, key)
        print("Getting information...")
        pages = json.loads(self.api._fetch('GET', '/pages.json').decode('ascii'))
        self.subdomain = re.search(r'(\w+).springnote.com',
                                   pages[0]['page']['uri']).group(1)

    def fetch(self, path, force=False):
        assert '..' not in path
        cache_path = os.path.normpath(
            os.path.join(SAVE_PATH, self.subdomain) + path)
        path += '?domain={}'.format(self.subdomain)
        if os.access(cache_path, os.F_OK):
            return open(cache_path, 'rb').read()
        makedirs(os.path.split(cache_path)[0], exist_ok=True)
        try:
            data = self.api._fetch('GET', path)
        except SpringnoteException as ex:
            if ex.status in [403, 404]:
                return None
            raise
        open(cache_path, 'wb+').write(data)
        return data

    def fetch_data(self, path):
        return json.loads(self.fetch(path).decode('ascii'))


def main():
    bot = Fetcher()
    subdomain = input("""백업할 스프링노트의 ID를 적어주세요.
(e.g. help.springnote.com -> help)
ID ({}) : """.format(bot.subdomain))
    if subdomain:
        bot.subdomain = subdomain
    subdomain = bot.subdomain
    makedirs(os.path.join(SAVE_PATH, subdomain), exist_ok=True)
    print("""주의: 다운로드는 정말 시간이 오래 걸립니다.
서버 상태에 따라 몇십 분에서 몇 시간이 걸릴 수 있습니다.""")
    try:
        print("Downloading profile image...")
        data = urlopen(
            'http://{}.springnote.com/profile_image'.format(subdomain)).read()
        open(os.path.join(SAVE_PATH, subdomain, 'profile_image.jpg'),
            'wb+').write(data)
    except:  # XXX probably 404
        pass
    try:
        xhtml = urlopen('http://{}.springnote.com/pages'.format(subdomain)).read()
        tree = lxml.html.fromstring(xhtml)
        note_title = tree.find('head').find('title').text_content()
        note_title = re.sub(unicode(r'(.*?) - '), unicode(''), note_title)
        open(os.path.join(SAVE_PATH, subdomain, 'note_title.txt'), 'wb+').write(
            note_title.strip().encode('utf8'))
        note_description = tree.cssselect('div.note-description')[0].text
        note_description = re.sub(unicode(r'\s+'), unicode(' '), note_description)
        open(os.path.join(SAVE_PATH, subdomain, 'note_description.txt'),
            'w+').write(note_description.strip().encode('utf8'))
    except:
        pass
    pages = bot.fetch_data('/pages.json')
    n_rev = n_att = 0
    print("{} / {} pages".format(0, len(pages)))
    for i, entry in enumerate(pages):
        id_ = entry['page']['identifier']
        bot.fetch('/pages/{}.json'.format(id_))
        for resource in ['collaboration', 'comments']:
            bot.fetch('/pages/{}/{}.json'.format(id_, resource))
        data = bot.fetch('/pages/{}/attachments.json'.format(id_))
        if data:
            attachments = json.loads(data.decode('ascii'))
            n = len(attachments)
            for k, _ in enumerate(attachments):
                bot.fetch('/pages/{}/attachments/{}'.format(id_,
                    _['attachment']['identifier']))
                if (k + 1) % 5 == 0:
                    print("{} / {} attachments".format(k + 1, n))
        data = bot.fetch('/pages/{}/revisions.json'.format(id_))
        if data:
            revisions = json.loads(data.decode('ascii'))
            n = len(revisions)
            for k, _ in enumerate(revisions):
                bot.fetch('/pages/{}/revisions/{}.json'.format(
                    id_, _['revision']['identifier']))
                if (k + 1) % 5 == 0:
                    print("{} / {} revisions".format(k + 1, n))
        print("{} / {} pages complete - {}".format(
            i + 1, len(pages),
            entry['page']['title'].encode('utf8', 'replace')))
    tags = json.loads(bot.fetch('/tags.json').decode('ascii'))
    print("Converted contents at: {}".format(SAVE_PATH))
    return
    print("{} / {} tags".format(0, len(tags)))
    for i, entry in enumerate(tags):
        id_ = entry['tag']['identifier']
        bot.fetch('/tag/{}.json'.format(id_))
        print("{} / {} tags".format(i + 1, len(tags)))


if __name__ == '__main__':
    main()