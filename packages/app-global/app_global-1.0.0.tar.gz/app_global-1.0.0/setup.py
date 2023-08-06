# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['app_global']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'app-global',
    'version': '1.0.0',
    'description': 'Sharing global variables between modules in a Python application',
    'long_description': '# app_global\n\nFrom [docs.python.org](https://docs.python.org/3/faq/programming.html?highlight=global#how-do-i-share-global-variables-across-modules):\n\n"The canonical way to share information across modules within a single program is to create a special module (often called config or cfg). Just import the config module in all modules of your application; the module then becomes available as a global name. Because there is only one instance of each module, any changes made to the module object get reflected everywhere. For example:"\n\n<br>\n\nSee /Example/app_global_test for an illustration that can be run in VSCode\n\n<br>\n\nAlthough not illustrated, it is recommended to categorize data within the app globals to keep organized and thus reduce possiblity obscure failure:\n* config.C - For global constants\n* config.G - For global application state like DB connections, caches etc.\n* config.opts - Application options\n* config.log - Application logger\n* config.printCli - Common print cli handler for clean exit during initialization\n\n<br>\n\nAs with any global data, care should be taken when using from within any multi threading applications. Use appropriate locking mechanisms as required.\n\n<br>\n\nBesides improving documentation, the main source `config.py` will be left as an empty source file so that is infinitely flexible',
    'author': 'Timothy C. Quinn',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/JavaScriptDude/app_global',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7.9,<4.0.0',
}


setup(**setup_kwargs)
