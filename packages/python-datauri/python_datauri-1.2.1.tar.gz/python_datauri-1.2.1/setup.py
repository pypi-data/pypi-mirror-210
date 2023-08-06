# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['datauri']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'python-datauri',
    'version': '1.2.1',
    'description': "A li'l class for data URI manipulation in Python",
    'long_description': "DataURI\n=======\n\n.. image:: https://github.com/fcurella/python-datauri/workflows/Python%20Tests/badge.svg\n    :target: https://github.com/fcurella/python-datauri/actions?query=workflow%3A%22Python+Tests%22\n    :alt: Build status of the master branch on Mac/Linux\n\n.. image:: https://coveralls.io/repos/github/fcurella/python-datauri/badge.svg?branch=master\n    :target: https://coveralls.io/github/fcurella/python-datauri?branch=master\n\nData URI manipulation made easy.\n\nThis isn't very robust, and will reject a number of valid data URIs. However, it meets the most useful case: a mimetype, a charset, and the base64 flag.\n\n\nInstallation\n------------\n\n.. code-block:: bash\n\n  $ pip install python-datauri\n\n\nParsing\n-------\n\n.. code-block:: python\n\n  >>> from datauri import DataURI\n  >>> uri = DataURI('data:text/plain;charset=utf-8;base64,VGhlIHF1aWNrIGJyb3duIGZveCBqdW1wZWQgb3ZlciB0aGUgbGF6eSBkb2cu')\n  >>> uri.mimetype\n  'text/plain'\n  >>> uri.charset\n  'utf-8'\n  >>> uri.is_base64\n  True\n  >>> uri.data\n  b'The quick brown fox jumped over the lazy dog.'\n\nNote that ``DataURI.data`` will always return bytes, (which in Python 2 is the same as a string).\nUse ``DataURI.text`` to get a string.\n\nCreating from a string\n----------------------\n\n.. code-block:: python\n\n  >>> from datauri import DataURI\n  >>> made = DataURI.make('text/plain', charset='us-ascii', base64=True, data='This is a message.')\n  >>> made\n  DataURI('data:text/plain;charset=us-ascii;base64,VGhpcyBpcyBhIG1lc3NhZ2Uu')\n  >>> made.data\n  b'This is a message.'\n\nCreating from a file\n--------------------\n\nThis is really just a convenience method.\n\n.. code-block:: python\n\n  >>> from datauri import DataURI\n  >>> png_uri = DataURI.from_file('somefile.png')\n  >>> png_uri.mimetype\n  'image/png'\n  >>> png_uri.data\n  b'\\x89PNG\\r\\n...'\n\nLicense\n-------\n\nThis code is released under the `Unlicense <http://unlicense.org/>`_.\n\nCredits\n-------\n\nThis is a repackaging of `this Gist <https://gist.github.com/zacharyvoase/5538178>`_\noriginally written by `Zachary Voase <https://github.com/zacharyvoase>`_.\n",
    'author': 'Flavio Curella',
    'author_email': 'flavio.curella@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
