# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['py_d2']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['example = py_d2.main:example']}

setup_kwargs = {
    'name': 'py-d2',
    'version': '1.0.0',
    'description': 'An unofficial, fully typed python interface for building .d2 graph files in python.',
    'long_description': '# py-d2\n\n![Banner](docs/images/banner.png)\n\nAn unofficial, fully typed python interface for building [.d2](https://github.com/terrastruct/d2) diagram files in python.\n\n## Installation\n\n```bash\npip install py-d2\n```\n\n## Usage\n\n```python\nfrom py_d2 import D2Diagram, D2Shape, D2Connection, D2Style\n\nshapes = [\n    D2Shape(name="shape_name1", style=D2Style(fill="red")),\n    D2Shape(name="shape_name2", style=D2Style(fill="blue"))]\nconnections = [\n    D2Connection(shape_1="shape_name1", shape_2="shape_name2")\n]\n\ndiagram = D2Diagram(shapes=shapes, connections=connections)\n\nwith open("graph.d2", "w", encoding="utf-8") as f:\n    f.write(str(diagram))\n\n```\n\nproduces the following graph.d2 file:\n\n```d2\n\nshape_name1: {\n  style: {\n    fill: red\n  }\n}\nshape_name2: {\n  style: {\n    fill: blue\n  }\n}\nshape_name1 -> shape_name2\n\n```\n\nThis can be rendered using `d2 graph.d2 graph.svg && open graph.svg` or [https://play.d2lang.com/](https://play.d2lang.com/) to produce\n\n![example graph](/docs/images/d2.svg)\n\nSee the [tests](/tests/test_py_d2) for more detailed usage examples.\n\n\n## Supported Features\n\n- [x] Shapes (nodes)\n- [x] Connections (links)\n- [x] Styles\n- [x] Containers (nodes/links in nodes)\n- [x] Shapes in shapes\n- [x] Arrow directions\n- [x] Markdown / block strings / code in shapes\n- [ ] Icons in shapes\n- [ ] SQL table shapes\n- [ ] Class shapes\n- [ ] Comments\n\n\n## Development\n### Prerequisite\n\n- [Python 3.7+](https://www.python.org/)\n- [Poetry 1.3](https://python-poetry.org/)\n- [pre-commit](https://pre-commit.com/)\n\n### Installation\n\nfollowing the steps below to setup the project:\n\n```bash\n\n```bash\n# Clone the repository\ngit clone git@github.com:MrBlenny/py-d2.git && cd py-d2\n\n# Install all dependencies\npoetry install --sync --all-extras --with dev,test,coverage\n\n# install git hook scripts for development\npre-commit install\n\n# Install dependencies with group \'dev\'、\'test\' for development\npoetry install --with dev,test\n# Only install required dependencies for production\npoetry install\n```\n\n### Usage\n\nThere are some useful commands for development:\n\n```bash\n# Run the example\npoetry run example\n\n# Debug with ipdb3\npoetry run ipdb3 ./src/py_d2/main.py\n\n# Code test\npoetry run pytest -s\n\n# Run default coverage test\npoetry run tox\n\n# Run example project coverage test at python 3.9 and 3.10\npoetry run tox -e py{39,310}-py-d2\n\n# Lint with black\npoetry run black ./src --check\n\n# Format code with black\npoetry run black ./src\n\n# Check with mypy\npoetry run mypy ./src\n\n# Check import order with isort\npoetry run isort ./src --check\n\n# Lint with flake8\npoetry run flake8 ./src\n```\n',
    'author': 'David Revay',
    'author_email': 'daverevay@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://mrblenny.github.io/py-d2/',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
