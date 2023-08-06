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
    'version': '0.1.1',
    'description': 'Jalali (Shamsi) calendar in your terminal, with holidays',
    'long_description': '#+TITLE: jalali-calendar-cli\n\n* Install\n#+begin_example bash\npip install -U jalali-calendar-cli\n#+end_example\n\n* Usage\n#+ATTR_HTML: :width 800\n[[file:readme.org_imgs/20230524_003016_h5V1Xf.png]]\n\n#+begin_example bash\nusage: jcal [-h] [--color {auto,always,never}]\n            [--true-color | --no-true-color] [--footnotes | --no-footnotes]\n            [--indentation INDENTATION]\n            [--holidays-json-path HOLIDAYS_JSON_PATH]\n            [month] [year]\n\npositional arguments:\n  month                 month in Jalali calendar (default: current month)\n  year                  year in Jalali calendar (default: current year)\n\noptions:\n  -h, --help            show this help message and exit\n  --color {auto,always,never}\n                        colorize the output\n  --true-color, --no-true-color\n                        enable true color support for output (default: False)\n  --footnotes, --no-footnotes\n                        show footnotes in the output (default: True)\n  --indentation INDENTATION\n                        number of spaces for indentation (default: 5)\n  --holidays-json-path HOLIDAYS_JSON_PATH\n                        path to JSON file containing holiday data\n#+end_example\n\n#+begin_example bash\njcal 12\n#+end_example\n\n#+begin_example\n            1402 Esfand           \n Sat  Sun  Mon  Tue  Wed  Thu  Fri\n                  1    2    3    4\n   5    6    7    8    9   10   11\n  12   13   14   15   16   17   18\n  19   20   21   22   23   24   25\n  26   27   28   29\n\n Holidays:\n   6: Birthday of Imam Mahdi\n   29: Nationalization of the Oil Industry\n#+end_example\n\n* Holidays Data\nThe default data dictionary is [[https://github.com/NightMachinery/jalali-calendar-cli/blob/master/jalali_calendar_cli/holidays.json][here]]. I plan to keep the data up-to-date, but you can always supply your own.\n\n',
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
