# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['folder_tree_generator']
setup_kwargs = {
    'name': 'folder-tree-generator',
    'version': '0.1.4',
    'description': 'Takes a folder path and outputs a text representation of the folders and files, supports ignore files.',
    'long_description': '# Folder Tree Generator\n\n\n[![PyPI version](https://badge.fury.io/py/folder-tree-generator.svg)](https://badge.fury.io/py/folder-tree-generator)\n\n![Test](https://github.com/seandearnaley/folder-tree-generator/workflows/Run%20pytest/badge.svg)\n\n\nFolder Tree Generator is a Python module that takes a folder path and outputs a text representation of the folders and files. It supports ignore files, such as `.gitignore`, to exclude certain files or folders from the output.\n\ntypical string output:\n\n```text\nmy_project/\n|-- .gitignore\n|-- main.py\n|-- utils.py\n|-- data/\n|   |-- input.txt\n|   |-- output.txt\n```\n\n## Why?\n\nI needed a way to generate folder structures in a standard text format that I could copy and paste into GPT without including all the build artifacts, eg. repository structures for code analysis.  If you wanted to make your own ignore file it should be a simple adapation of a gitignore file, in 90% of my use cases, the gitignore is sufficient.\n\n## Installation\n\nYou can install the module from PyPI using pip:\n\n```bash\npip install folder-tree-generator\n```\n\n## Usage\n\nYou can use the module as a command-line tool or import it in your Python script.\n\n### Command-line usage\n\n```bash\npython -m folder_tree_generator /path/to/your/folder\n```\n\n### Python script usage\n\n```python\nfrom folder_tree_generator import generate_tree\n\noutput_text = generate_tree("/path/to/your/folder")\nprint(output_text)\n```\n\n## Configuration\n\nBy default, the module looks for a `.gitignore` file in the root folder to determine which files and folders to ignore. You can change the ignore file name by passing an optional argument to the `generate_tree` function:\n\n```python\noutput_text = generate_tree("/path/to/your/folder", ignore_file_name=".myignore")\n```\n\n## Development\n\nTo set up the development environment, clone the repository and install the required dependencies using Poetry:\n\n```bash\ngit clone https://github.com/seandearnaley/folder-tree-generator.git\ncd folder-tree-generator\npoetry install\n```\n\nTo run the tests, use the following command:\n\n```bash\npoetry run pytest\n```\n\nMake sure to update the README.md file with these changes.\n\n## Contributing\n\nContributions are welcome! Please feel free to submit a pull request or open an issue on the [GitHub repository](https://github.com/seandearnaley/folder-tree-generator).\n\n## License\n\nThis project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.',
    'author': 'Sean Dearnaley',
    'author_email': 'SeanDearnaley@outlook.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'py_modules': modules,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
