from distutils.core import setup
import glob

import py2exe

setup(
    console=['shell.py'],
    options={
        'py2exe': {
            'skip_archive': True,
            'includes': [
                'idlelib',
                'idlelib.AutoComplete',
                'idlelib.AutoExpand',
                'idlelib.CallTips',
                'idlelib.FormatParagraph',
                'idlelib.ParenMatch',
                'idlelib.ScriptBinding',
                'lxml._elementpath',
            ],
        },
    },
    data_files=[
        ('.', (
            ['run.py'] +
            glob.glob('C:\\Python27\\Lib\\idlelib\\config-*.def')
        )),
    ],
)