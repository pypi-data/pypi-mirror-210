# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ebdesk_email_executor',
 'ebdesk_email_executor.config',
 'ebdesk_email_executor.model',
 'ebdesk_email_executor.route']

package_data = \
{'': ['*']}

install_requires = \
['pymongo>=4.0.1,<5.0.0', 'redis>=4.5.5,<5.0.0', 'uvicorn>=0.17.4,<0.18.0']

setup_kwargs = {
    'name': 'ebdesk-email-executor',
    'version': '0.1.27',
    'description': '',
    'long_description': '# Ebdesk Google Account Management\n\n### How To Install\n```python\npip install --trusted-host 192.168.20.26 --index-url http://192.168.20.26:6060/simple/ ebdesk-email-executor\n```\n\n### Example \n\n##### Get one email\n```python\nfrom ebdesk_email_executor.main import ExecutorAccount\nex = ExecutorAccount()\n\ndata = ex.get_email()\n#return {\'email\': \'nasri@mail.com\', \'password\': \'sirrah\', \'status\': \'ACTIVE\', \'active\': False}\n```\n\n##### Bulk Email\n```python\nfrom ebdesk_email_executor.main import ExecutorAccount\nex = ExecutorAccount()\n\ntemp = [{\n    "email": "nasri@mail.com",\n    "password": "sirrah",\n    "status": "ACTIVE",\n    "active": False\n},{\n    "email": "nasri1@mail.com",\n    "password": "sirrah",\n    "status": "ACTIVE",\n    "active": False\n},{\n    "email": "nasri2@mail.com",\n    "password": "sirrah",\n    "status": "ACTIVE",\n    "active": False\n}]\nex.bulk_email(model=temp)\n```\n\n##### Add Email (single)\n```python\nfrom ebdesk_email_executor.main import ExecutorAccount\nex = ExecutorAccount()\n\nex.add_email(email="email@mail.com", password="rahasia2023", status="ACTIVE")\n```\n\n##### Update Active Status\nafter execute chat gpt, use this function to update status active into `False`, to usable email \n```python\nfrom ebdesk_email_executor.main import ExecutorAccount\nex = ExecutorAccount()\n\nex.update_active("email@mail.com")\n```\n\n##### Handle Timeout\nif account has blocket from open api, use this function\n```python\nfrom ebdesk_email_executor.main import ExecutorAccount\nex = ExecutorAccount()\n\nex.update_active("email@mail.com")\n```\n\n',
    'author': 'Nasri Adzlani',
    'author_email': 'nasri@jkt1.ebdesk.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
