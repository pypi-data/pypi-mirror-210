# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['canaveral_cli']

package_data = \
{'': ['*'],
 'canaveral_cli': ['data/*',
                   'data/oam_types/component/*',
                   'data/oam_types/policy/*',
                   'data/oam_types/trait/*',
                   'data/oam_types/workflowstep/*',
                   'data/templates/*']}

install_requires = \
['Jinja2>=3.1.2,<4.0.0',
 'PyGithub>=1.58.2,<2.0.0',
 'PyYAML>=6.0,<7.0',
 'inquirerpy>=0.3.4,<0.4.0',
 'python-dotenv>=1.0.0,<2.0.0',
 'rich>=13.3.5,<14.0.0',
 'typer[all]>=0.9.0,<0.10.0']

entry_points = \
{'console_scripts': ['canaveral = canaveral_cli.cli:app']}

setup_kwargs = {
    'name': 'canaveral-cli',
    'version': '0.1.6',
    'description': "Helper CLI to interact with Devscope's internal platform codename Canaveral",
    'long_description': '# Canaveral CLI\n\nThis Project uses [Typer](https://typer.tiangolo.com/) for the CLI functionality and [InquirerPy](https://inquirerpy.readthedocs.io/en/latest/index.html#) for the parameter selection\n\n## Run it\nWorking with virtual envs in Python:\n- https://realpython.com/python-virtual-environments-a-primer\n- https://aaronlelevier.github.io/virtualenv-cheatsheet/\n\n```bash\n$ python3 -m venv venv --prompt="canaveral-env"\n$ source venv/bin/activate\n(canaveral-env) $ \n(canaveral-env) $ deactivate\n$ \n$ pip install -r requirements.txt\n$ OR\n$ python -m pip install -r requirements.txt\n```\n\n## How to contribuite\nProject layout to adhere to:\n- https://realpython.com/python-application-layouts/#command-line-application-layouts\n\n## Internal Notes\n\nDevscope Internal notes and documentation avaible at [Canaveral](https://devscope365.sharepoint.com/sites/academy/_layouts/OneNote.aspx?id=%2Fsites%2Facademy%2FSiteAssets%2FAcademy%20Notebook&wd=target%282023.one%7C1069493A-33E1-4F4C-8D77-28AA9AE54494%2FCanaveral%20CLI%7CF359B855-A8C4-4DB9-B416-CA0D700F2904%2F%29)\n',
    'author': 'André Gomes',
    'author_email': 'andre.gomes@devscope.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/DevScope/canaveral-cli',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
