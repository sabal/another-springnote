from distutils.core import setup
import glob

import py2exe

setup(
    windows=[{
        'script': 'shell.py',
        'icon_resources': [(0, 'C:\\Python27\\Lib\\site-packages\\win32\\test\\'
            'win32rcparser\\python.ico')],
    }],
    options={
        'py2exe': {
            'bundle_files': 3,  # static linking causes error
            'skip_archive': False,
            'includes': [
                'idlelib',
                'idlelib.AutoComplete',
                'idlelib.AutoExpand',
                'idlelib.CallTips',
                'idlelib.FormatParagraph',
                'idlelib.ParenMatch',
                'idlelib.ScriptBinding',
                'lxml._elementpath',

                'convert_html',
                'convert_dokuwiki_sabal',
                'fetch_springnote',
            ],
        },
    },
    data_files=[
        ('.', (
            [
                'run.py',
                'sabal.css',
            ] +
            glob.glob('C:\\Python27\\Lib\\idlelib\\config-*.def')
        )),
    ],
    zipfile=None,
)
