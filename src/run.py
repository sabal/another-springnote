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
Springnote converter
""" +
'=' * 80 +
"""
Choose option / 다음 중 선택하십시오:
1) Convert to HTML / HTML로 변환
2) Convert to MediaWiki / MediaWiki로 변환
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
            import convert_html
            convert_html.main()
        elif cmd in ['2']:
            import convert_mediawiki
            convert_mediawiki.main()
        elif cmd in ['test']:
            import convert_dokuwiki_sabal
            convert_dokuwiki_sabal.main()
        else:
            continue
        print("Completed.")
        input("Press [enter]: ")
        print welcome_message


if __name__ == '__main__':
    main()
