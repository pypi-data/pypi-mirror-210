# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['blackarrow', 'blackarrow.test']

package_data = \
{'': ['*']}

install_requires = \
['fabulous>=0.4.0,<0.5.0']

entry_points = \
{'console_scripts': ['ba = blackarrow:main', 'blackarrow = blackarrow:main']}

setup_kwargs = {
    'name': 'blackarrow',
    'version': '1.1',
    'description': 'A fast keyword searcher',
    'long_description': '"Universal" Text Finder\n=======================\n\n[![Test Status](https://travis-ci.org/TheDataLeek/black-arrow.svg?branch=master)](https://travis-ci.org/TheDataLeek/black-arrow)\n[![Coverage Status](https://coveralls.io/repos/github/TheDataLeek/black-arrow/badge.svg?branch=master)](https://coveralls.io/github/TheDataLeek/black-arrow?branch=master)\n\nIt\'s basically just grep in python... Nothing fancy, just an easy extensible way\nto find things....\n\nYeah, I know, it\'s "reinventing the wheel" but ehhh, this is easier to extend to\ncover any and all weird cases without having to memorize a bunch of obscure\ncombinations of bash commands.\n\nThat out of the way, let\'s talk about what this *actually does*...\n\n## Quick Overview\n\nEssentially Black Arrow (or `ba` for short) is a way to search through every line in every file and\nfind matching keyword *or* regular expressions. It uses smart case, so if the search term is all\nlowercase it defaults to case-insensitive (mostly for ease of use).\n\n![png](./img/demo.png)\n\nYou can also supply it with regular expressions and it handles them natively.\n\n![png](./img/demo2.png)\n\nOther features include -\n\n* excluding certain files or paths,\n* replacing any matches that have been found,\n* specifying the max depth to search (good for large directory structures),\n* "pipe" mode for unix piping,\n* open the files in the `$EDITOR` for manual parsing. \n\n## Installation\n\n```\n┬─[zoe@fillory:~/Dropbox/Projects/black-arrow]─[09:22:12 PM]\n╰─>$ pip install --user blackarrow\n```\n\n## Black-Arrow Script\n\n```bash\n┬─[zoe@fillory:~/Dropbox/Projects/black-arrow]─[09:33:40 PM]\n╰─>$ ./black-arrow/blackarrow.py -h\nusage: ba [-h] [-d DIRECTORIES [DIRECTORIES ...]] [-i IGNORE [IGNORE ...]]\n          [-f FILENAME [FILENAME ...]] [-w WORKERS] [-p] [-e] [-l]\n          [-r REPLACE] [-D DEPTH] [--dev]\n          R\n\npositional arguments:\n  R                     Search term (regular expression)\n\noptional arguments:\n  -h, --help            show this help message and exit\n  -d DIRECTORIES [DIRECTORIES ...], --directories DIRECTORIES [DIRECTORIES ...]\n                        Director(y|ies) to run against\n  -i IGNORE [IGNORE ...], --ignore IGNORE [IGNORE ...]\n                        Things to ignore (regular expressions)\n  -f FILENAME [FILENAME ...], --filename FILENAME [FILENAME ...]\n                        Filename search term(s)\n  -w WORKERS, --workers WORKERS\n                        Number of workers to use (default numcores, with\n                        fallback 6 unless set)\n  -p, --pipe            Run in "pipe" mode with brief output\n  -e, --edit            Edit the files?\n  -l, --lower           Check strict lower case?\n  -r REPLACE, --replace REPLACE\n                        Replace text found in place with supplied\n  -D DEPTH, --depth DEPTH\n                        Directory depth to search in\n  --dev                 Run in development mode (NO OUTPUT)\n```\n\n#### The Name\n\n*"Arrow! Black arrow! I have saved you to the last. You have never failed me and\nI have always recovered you. I had you from my father and he from of old. If\never you came from the forges of the true king under the Mountain, go now and\nspeed well!"*\n\n― J.R.R. Tolkien, The Hobbit\n',
    'author': 'Zoe Farmer',
    'author_email': 'zoe@dataleek.io',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/TheDataLeek/black-arrow',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
