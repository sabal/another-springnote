from distutils.core import setup

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
        ('.', [
            'run.py',
            'config-extensions.def',
            'config-highlight.def',
            'config-keys.def',
            'config-main.def',
        ]),
    ],
)