# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['metabypass']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'metabypass',
    'version': '0.0.4',
    'description': 'metabypass',
    'long_description': "\nCLIENT_ID = 'YOUR_CLIENT_ID'  # ****CHANGE HERE WITH YOUR VALUE*******\n\nCLIENT_SECRET = 'YOUR_SECRET_KEY'  # ****CHANGE HERE WITH YOUR VALUE*******\n\nEMAIL = 'YOUR_ACCOUNT_EMAIL'  # ****CHANGE HERE WITH YOUR VALUE*******\n\nPASSWORD = 'YOUR_ACCOUNT_PASSWORD'  # ****CHANGE HERE WITH YOUR VALUE*******\n\ncred=getCredentials(CLIENT_ID,CLIENT_SECRET,EMAIL,PASSWORD)\n\n",
    'author': 'ad',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
}


setup(**setup_kwargs)
