# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': '.'}

packages = \
['deez_py']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'deez-py',
    'version': '0.1.3',
    'description': 'A Python implementation of a lexical analyzer that provides comprehensive scanning, and lookahead capabilities.',
    'long_description': '=========\ndeez_py\n=========\n\n.. image:: https://img.shields.io/badge/License-GPLv3-blue.svg\n   :target: https://github.com/ThePrimeagen/ts-rust-zig-deez_py/tree/master/python/LICENSE\n   :alt: License\n\n.. image:: https://img.shields.io/pypi/v/deez_py.svg\n   :target: https://pypi.org/project/deez_py/\n   :alt: pypi version\n\n**deez_py** is a Python implementation of a lexical analyzer that provides comprehensive scanning, and lookahead capabilities.\n\n🛠️ Requirements\n---------------\n\n**deez_py** requires Python 3.9 or above.\n\nTo install Python 3.9, I recommend using `pyenv`_.\n\n.. code-block:: bash\n\n   # install pyenv\n   git clone https://github.com/pyenv/pyenv ~/.pyenv\n\n   # setup pyenv (you should also put these three lines in .bashrc or similar)\n   # if you are using zsh\n   cat << EOF >> ~/.zshrc\n   # pyenv config\n   export PATH="${HOME}/.pyenv/bin:${PATH}"\n   export PYENV_ROOT="${HOME}/.pyenv"\n   eval "$(pyenv init -)"\n   EOF\n\n   # or if you using the default bash shell, do this instead:\n   cat << EOF >> ~/.bashrc\n   # pyenv config\n   export PATH="${HOME}/.pyenv/bin:${PATH}"\n   export PYENV_ROOT="${HOME}/.pyenv"\n   eval "$(pyenv init -)"\n   EOF\n   # Close and open a new shell session\n   # install Python 3.9.10\n   pyenv install 3.9.10\n\n   # make it available globally\n   pyenv global system 3.9.10\n\n\nTo manage the Python 3.9 virtualenv, I recommend using `poetry`_.\n\n.. code-block:: bash\n\n   # install poetry\n   curl -sSL https://install.python-poetry.org | python3 -\n   poetry --version\n   Poetry version 1.1.13\n\n   # Having the python executable in your PATH, you can use it:\n   poetry env use 3.9.10\n\n   # However, you are most likely to get the following issue:\n   Creating virtualenv deez_py-dxc671ba-py3.9 in ~/.cache/pypoetry/virtualenvs\n\n   ModuleNotFoundError\n\n   No module named \'virtualenv.seed.via_app_data\'\n\n   at <frozen importlib._bootstrap>:973 in _find_and_load_unlocked\n\n   # To resolve it, you need to reinstall virtualenv through pip\n   sudo apt remove --purge python3-virtualenv virtualenv\n   python3 -m pip install -U virtualenv\n\n   # Now, you can just use the minor Python version in this case:\n   poetry env use 3.9.10\n   Using virtualenv: ~/.cache/pypoetry/virtualenvs/deez_py-dxc671ba-py3.9\n\n\n🚨 Installation\n---------------\n\nWith :code:`pip`:\n\n.. code-block:: console\n\n   python3 -m pip install deez-py\n\n\n🚸 Usage\n--------\n\n.. code-block:: python3\n\n   >>> from deez_py import Lexer\n   >>> lex = Lexer(\'=+(){},;\')\n   >>> for _ in range(9):\n   >>>     print(lex.get_next_token())\n   ... \n   Token(type=<TokenType.Equal: \'=\'>, literal=\'=\')\n   Token(type=<TokenType.Plus: \'+\'>, literal=\'+\')\n   Token(type=<TokenType.LParen: \'(\'>, literal=\'(\')\n   Token(type=<TokenType.RParen: \')\'>, literal=\')\')\n   Token(type=<TokenType.LSquirly: \'{\'>, literal=\'{\')\n   Token(type=<TokenType.RSquirly: \'}\'>, literal=\'}\')\n   Token(type=<TokenType.Comma: \',\'>, literal=\',\')\n   Token(type=<TokenType.Semicolon: \';\'>, literal=\';\')\n   Token(type=<TokenType.Eof: \'EOF\'>, literal=\'EOF\')\n\n\n📝 License\n----------\n\nTodo.\n\n.. _pyenv: https://github.com/pyenv/pyenv\n.. _poetry: https://github.com/python-poetry/poetry\n',
    'author': 'Mahmoud Harmouch',
    'author_email': 'business@wiseai.dev',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/ThePrimeagen/ts-rust-zig-deez',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
