# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mecapacktools']

package_data = \
{'': ['*']}

install_requires = \
['arrow>=1.2.3,<2.0.0', 'sortedcontainers>=2.4.0,<3.0.0']

extras_require = \
{'excel': ['openpyxl>=3.1.2,<4.0.0', 'pywin32>=306,<307'],
 'sql': ['pypyodbc>=1.3.6,<2.0.0'],
 'webservices': ['requests>=2.28.2,<3.0.0',
                 'suds>=1.1.2,<2.0.0',
                 'xmltodict>=0.13.0,<0.14.0']}

setup_kwargs = {
    'name': 'mecapacktools',
    'version': '1.0.2',
    'description': '',
    'long_description': '# Tools for Mecapack\n\nLa doc est disponible en Html ou en MD\n\n## installation par pip\n\n`pip install mecapacktools`\n\nInstaller les extensions :\n\n`pip install mecapacktools[excel,sql,webservices]`\n\n### Extensions diponibles :\n\n- excel \n- Sql \n- WebServices \n\n## Notes pour le développement:\n\n### Installation\n\n`poetry install --with dev --all-extras`\n\n### Génération de la doc\n\n`poetry run .\\make.bat html`\n`poetry run .\\make.bat markdown`\n\n### Publier une nouvelle version\n\nChanger la version :\nDans le fichier pyproject.toml modifier :\n```\n[tool.poetry]\nversion = "1.0.0"\n ```\n\nPublier sur pypi `poetry publish --build`\n\n\n\n',
    'author': 'Informatique Mecapack',
    'author_email': 'informatique@mecapack.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
