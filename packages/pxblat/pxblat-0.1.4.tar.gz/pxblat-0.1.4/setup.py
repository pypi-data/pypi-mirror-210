# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['pxblat', 'pxblat.cli', 'pxblat.extc', 'pxblat.server']

package_data = \
{'': ['*'],
 'pxblat.extc': ['bindings/*',
                 'bindings/binder/*',
                 'include/*',
                 'include/aux/*',
                 'include/core/*',
                 'include/net/*',
                 'src/*',
                 'src/aux/*',
                 'src/core/*',
                 'src/net/*']}

install_requires = \
['biopython>=1.81,<2.0',
 'deprecated>=1.2.13,<2.0.0',
 'loguru>=0.7.0,<0.8.0',
 'mashumaro>=3.7,<4.0',
 'pybind11>=2.10.4,<3.0.0',
 'pysimdjson>=5.0.2,<6.0.0',
 'rich>=13.3.5,<14.0.0',
 'setuptools>=67.7.2,<68.0.0',
 'typer>=0.9.0,<0.10.0']

entry_points = \
{'console_scripts': ['pxblat = pxblat.cli.cli:app']}

setup_kwargs = {
    'name': 'pxblat',
    'version': '0.1.4',
    'description': 'A native python binding for blat suit',
    'long_description': '# PxBLAT: An Efficient and Ergonomics Python Binding Library for BLAT\n\n[![python](https://img.shields.io/badge/Python-3776AB.svg?style=for-the-badge&logo=Python&logoColor=white)](https://www.python.org/)\n[![c++](https://img.shields.io/badge/C++-00599C.svg?style=for-the-badge&logo=C++&logoColor=white)](https://en.cppreference.com/w/)\n[![c](https://img.shields.io/badge/C-A8B9CC.svg?style=for-the-badge&logo=C&logoColor=black)](https://www.gnu.org/software/gnu-c-manual/)\n[![pypi](https://img.shields.io/pypi/v/pxblat.svg?style=for-the-badge)](https://pypi.org/project/pxblat/)\n[![pyversion](https://img.shields.io/pypi/pyversions/pxblat?style=for-the-badge)](https://pypi.org/project/pxblat/)\n[![license](https://img.shields.io/pypi/l/pxblat?style=for-the-badge)](https://opensource.org/licenses/mit)\n[![precommit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?style=for-the-badge&logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)\n[![black](https://img.shields.io/badge/code%20style-black-000000.svg?style=for-the-badge)](https://github.com/psf/black)\n[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v1.json&style=for-the-badge)](https://github.com/charliermarsh/ruff)\n[![download](https://img.shields.io/pypi/dm/pxblat?style=for-the-badge)](https://pypi.org/project/pxblat/)\n[![Codecov](https://img.shields.io/codecov/c/github/cauliyang/pxblat/main?style=for-the-badge&token=71639758-1cb2-48ed-a3b6-a79c60e568a5)](https://app.codecov.io/gh/cauliyang/pxblat)\n[![lastcommit](https://img.shields.io/github/last-commit/cauliyang/pxblat?style=for-the-badge)](https://github.com/cauliyang/pxblat/)\n[![tests](https://github.com/cauliyang/pxblat/actions/workflows/tests.yml/badge.svg?style=for-the-badge)](https://github.com/cauliyang/pxblat/actions/workflows/tests.yml)\n\n---\n\n## 📚 Table of Contents\n\n- [📚 Table of Contents](#-table-of-contents)\n- [📍Overview](#-introdcution)\n- [🔮 Features](#-features)\n- [🏎💨 Getting Started](#-getting-started)\n- [🤝 Contributing](#-contributing)\n- [\U0001faaa License](#-license)\n- [📫 Contact](#-contact)\n- [🙏 Acknowledgments](#-acknowledgments)\n\n---\n\n## 🔮 Feautres\n\n- no intermidiate files, all in memory\n- no system call\n- no need to bother with log files to get status of tool\n- no need to worry about file format\n- no other dependency\n- higher proformance and Ergonomics (compare with current blat endpoint)\n\n## TODO\n\n- [x] parser gfclient result\n- [x] parse gfserver query result\n- [x] multi-connection server\n- [ ] benchmarking multi connection and original version\n- [x] test result with original version\n- [x] fix build.py to build ssl, hts, maybe libuv when install with pip\n- [ ] add tool to conda channel\n- [ ] add too to dokerhub\n- [ ] add tool to pip\n- [ ] change abort to throw exceptions\n\n---\n\n<img src="https://raw.githubusercontent.com/PKief/vscode-material-icon-theme/ec559a9f6bfd399b82bb44393651661b08aaf7ba/icons/folder-src-open.svg" width="80" />\n\n## 🚀 Getting Started\n\n### ✅ Prerequisites\n\nBefore you begin, ensure that you have the following prerequisites installed:\n\n> `[📌  INSERT-PROJECT-PREREQUISITES]`\n\n### 💻 Installation\n\n1. Clone the pxblat repository:\n\n```sh\ngit clone https://github.com/cauliyang/pxblat.git\n```\n\n2. Change to the project directory:\n\n```sh\ncd pxblat\n```\n\n3. Install the dependencies:\n\n```sh\npoetry install\n```\n\n### 🤖 Using pxblat\n\n```sh\npxblat\n```\n\n### 🧪 Running Tests\n\n```sh\npytest\n```\n\n<hr />\n\n## 🛠 Future Development\n\n- [x] [📌 COMPLETED-TASK]\n- [ ] [📌 INSERT-TASK]\n- [ ] [📌 INSERT-TASK]\n\n---\n\n## 🤝 Contributing\n\nContributions are always welcome! Please follow these steps:\n\n1. Fork the project repository. This creates a copy of the project on your account that you can modify without affecting the original project.\n2. Clone the forked repository to your local machine using a Git client like Git or GitHub Desktop.\n3. Create a new branch with a descriptive name (e.g., `new-feature-branch` or `bugfix-issue-123`).\n\n```sh\ngit checkout -b new-feature-branch\n```\n\n4. Make changes to the project\'s codebase.\n5. Commit your changes to your local branch with a clear commit message that explains the changes you\'ve made.\n\n```sh\ngit commit -m \'Implemented new feature.\'\n```\n\n6. Push your changes to your forked repository on GitHub using the following command\n\n```sh\ngit push origin new-feature-branch\n```\n\n7. Create a pull request to the original repository.\n   Open a new pull request to the original project repository. In the pull request, describe the changes you\'ve made and why they\'re necessary.\n   The project maintainers will review your changes and provide feedback or merge them into the main branch.\n\n---\n\n## \U0001faaa License\n\nThis project is licensed under the `[📌  INSERT-LICENSE-TYPE]` License. See the [LICENSE](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/adding-a-license-to-a-repository) file for additional info.\n\n---\n\n## 🙏 Acknowledgments\n\n[📌 INSERT-DESCRIPTION]\n\n---\n',
    'author': 'Yangyang Li',
    'author_email': 'yangyang.li@northwestern.edu',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}
from build import *
build(setup_kwargs)

setup(**setup_kwargs)
