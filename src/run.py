# coding: utf-8
try:
    raw_input
    input = raw_input
except:
    pass


def main():
    try:
        # Change IDLE encoding
        import sys
        sys.stdout.encoding = 'utf8'
    except TypeError:
        pass

    welcome_message = (
'=' * 80 +
"""
Another Springnote
""" +
'=' * 80 +
"""
Choose option / 다음 중 선택하십시오:
1) Back up Springnote 스프링노트 백업
2) Convert your backup to other format / 백업한 스프링노트를 다른 형식으로 변환
0) Quit / 종료
""" +
'=' * 80)
    print welcome_message
    while True:
        cmd = input("> ")
        cmd = cmd.strip()
        if cmd in ['0']:
            print("Closing the program.  Close the window or press ctrl-d.")
            return
        elif cmd in ['1']:
            import fetch_springnote
            fetch_springnote.main()
            print("Completed.")
            input("Press enter key: ")
        elif cmd in ['2']:
            convert_main()
            print welcome_message


def convert_main():
    print (
'=' * 80 +
"""
Another Springnote > 변환
""" +
'=' * 80 +
"""
Choose option / 다음 중 선택하십시오:
1) Convert to HTML / HTML로 변환
0) Exit from this menu / 이 메뉴 나가기
""" +
'=' * 80)
    while True:
        cmd = input("> ")
        cmd = cmd.strip()
        if cmd in ['0']:
            return
        elif cmd in ['1']:
            import convert_html
            convert_html.main()
            print("Completed.")
            input("Press [enter]: ")
            return
        elif cmd in ['test']:
            import convert_dokuwiki_sabal
            convert_dokuwiki_sabal.main()
            print("Completed.")
            input("Press [enter]: ")
            return


if __name__ == '__main__':
    main()