# coding: utf-8
import convert_dokuwiki
import fetch_springnote


def main():
    while True:
        welcome_message = (
'=' * 80 +
"""
Another Springnote
""" +
'=' * 80 +
"""
Choose option / 다음 중 선택하십시오:
1) Back up Springnote 스프링노트 백업
2) Convert your backup to DokuWiki / 백업을 DokuWiki로 변환
3) Install converted DokuWiki / 변환된 DokuWiki 설치
Close the Window when you're done. / 종료하시려면, 그냥 창을 꺼 주세요.
""" +
'=' * 80 +
"""
> """)
        cmd = raw_input(welcome_message)
        cmd = cmd.strip()
        if cmd in ['1']:
            fetch_springnote.main()
        elif cmd in ['2']:
            convert_dokuwiki.main()


if __name__ == '__main__':
    main()
