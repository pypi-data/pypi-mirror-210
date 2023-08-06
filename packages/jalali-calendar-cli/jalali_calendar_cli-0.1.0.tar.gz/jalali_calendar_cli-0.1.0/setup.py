# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['jalali_calendar_cli']

package_data = \
{'': ['*']}

install_requires = \
['colorama>=0.4.6,<0.5.0', 'jdatetime>=4.1.1,<5.0.0']

entry_points = \
{'console_scripts': ['jalali-calendar = '
                     'jalali_calendar_cli.jalali_calendar:main',
                     'jcal = jalali_calendar_cli.jalali_calendar:main']}

setup_kwargs = {
    'name': 'jalali-calendar-cli',
    'version': '0.1.0',
    'description': '',
    'long_description': '#+TITLE: jalali-calendar-cli\n\n* Install\n#+begin_example zsh\n\n#+end_example\n',
    'author': 'NightMachinery',
    'author_email': 'feraidoonmehri@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
