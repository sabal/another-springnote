# (개발자를 위한) 사용법

## 1. 스프링노트 백업

    $ ./fetch-springnote.py
    Your OpenID (like http://example.myid.net/) : http://puzzlet.myid.net/
    Go to following URL and get the user key:
    https://api.openmaru.com/delegate_key/springnote?app_id=71fcb7c8&openid=http://puzzlet.myid.net/
    Key: abcdef1234567890
    Connecting...
    347 / 347 pages  2347 / 2347 revisions  79 / 79 attachments
    $

## 2. DokuWiki로 변환

- 아직 완벽하게 변환이 안 됩니다.
- 특히 비공개 페이지 권한 같은 거 아직 안 막혀 있습니다.

    $ ./convert-dokuwiki.py 
    347 / 347 pages
    $

## 3. DokuWiki 설치

    $ ./make.py 
    INFO:root:Extracting DokuWiki...
    INFO:root:Extracting fckgLite plugin...
    $ mv "build_linux2/Another Springnote" ~/public_html/my_wiki
    $

# 라이선스

- DokuWiki - GPLv2
 - fckgLite 플러그인 - GPLv2
- nginx - BSD-like
- PHP - PHP License
