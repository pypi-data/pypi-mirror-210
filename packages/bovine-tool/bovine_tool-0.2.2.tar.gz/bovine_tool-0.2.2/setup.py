# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bovine_tool']

package_data = \
{'': ['*']}

install_requires = \
['bovine-store>=0.2.1,<0.3.0']

setup_kwargs = {
    'name': 'bovine-tool',
    'version': '0.2.2',
    'description': 'Basic tools to administrate a bovine herd',
    'long_description': '# bovine_tool\n\nbovine_tool provides a CLI interface to manage bovine.\n\n## Configuration\n\nThe default database connection is "sqlite://bovine.sqlite3". This can be overwridden with the environment variable "BOVINE_DB_URL".\n\n## Quick start\n\nTo register a new user with a FediVerse handle use\n\n```bash\npython -m bovine_tool.register fediverse_handle [--domain DOMAIN]\n```\n\nthe domain must be specified.\n\n## Managing users\n\n```bash\npython -m bovine_tool.manage bovine_name\n```\n\ndisplays the user.\n\nTo add a did key for [the Moo Client Registration Flow](https://blog.mymath.rocks/2023-03-25/BIN2_Moo_Client_Registration_Flow) with a BovineClient use\n\n```bash\npython -m bovine_tool.manage bovine_name --did_key key_name did_key\n```\n\nFurthermore, using `--properties` the properties can be over written.\n\n## Todo\n\n- [ ] Add ability to delete stale data, e.g. remote data older than X days\n- [ ] Add ability to import/export all data associated with an actor\n',
    'author': 'Helge',
    'author_email': 'helge.krueger@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://codeberg.org/bovine/bovine',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
