# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['pretty_python']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'pretty-python',
    'version': '0.1.0',
    'description': 'A Python library for pretty printing Python data structures',
    'long_description': '# pretty_python\n\nStandard Python Shim for IPython pretty library\n\nSee [lib.pretty Docs](https://ipython.readthedocs.io/en/stable/api/generated/IPython.lib.pretty.html#) for full api.\n\nOnly differnce to use this is to import as follows:\n```\nfrom pretty_python import pretty, pprint\n\nd = dict(Foo=[1,2,3], Bar={\'a\':1, \'b\':2, \'c\':3})\n\nprint(f"my dict: {pretty(d)}")\n\n# -or-\n\npprint(d)\n```\n\nIf running within IPython / Jupyter Notebook, it will load the builtin pretty library, otherwise it will load this fork which removes IPython dependency',
    'author': 'IPython Team',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/JavaScriptDude/pretty_python',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7.9,<4.0.0',
}


setup(**setup_kwargs)
