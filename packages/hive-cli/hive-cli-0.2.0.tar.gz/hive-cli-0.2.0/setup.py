# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['hive']

package_data = \
{'': ['*']}

install_requires = \
['Pillow>=9.5.0,<10.0.0',
 'PyPDF2>=3.0.1,<4.0.0',
 'qdrant-client>=1.1.7,<2.0.0',
 'sentence-transformers>=2.2.2,<3.0.0',
 'torch>=2.0.1,<3.0.0',
 'typer[all]>=0.9.0,<0.10.0']

entry_points = \
{'console_scripts': ['hive = hive.cli:app']}

setup_kwargs = {
    'name': 'hive-cli',
    'version': '0.2.0',
    'description': '',
    'long_description': '<p align="center">\n  <img height="175" src="https://github.com/PPierzc/hive/blob/main/docs/logo.png" alt="Qdrant">\n</p>\n\n<p align="center">\n    <b>Unleash the power of Hive and navigate your knowledge base like a busy bee!  🐝🔍✨</b>\n</p>\n\n<p align="center">\n<a href="https://github.com/psf/black"><img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Black Code Style"></a>\n<a href="https://github.com/ppierzc/hive/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License"></a>\n</p>\n\n🐝 Hive is a CLI tool for semantic searching of your knowledge base 📚. It allows you to easily search through your collection of files and directories, extracting meaningful information based on your prompts.\n No more searching through haystacks—let Hive find the golden honey! 🍯🐝 Embrace the buzz and let your knowledge thrive! 🚀💡\n\n## Getting Started\n\n### Installation\nYou can install Hive using pip:\n\n```shell\npip install hive-cli\n```\n\n### Initializing Hive\nTo get started with Hive, initialize it in your project directory using the following command:\n\n```shell\nhive init\n```\nThis sets up Hive and creates the necessary configuration files to enable knowledge base searching.\n\n### Adding Files or Directories\nYou can add files or directories to your Hive knowledge base using the add command:\n\n```shell\nhive add <file_or_dir_to_add>\n```\nThis command allows Hive to index and analyze the content of the specified files or directories, making them searchable within your knowledge base.\n\n#### Supported File Types\nHive currently supports only Markdown and PDF files. Support for other file types is coming soon!\n\n### Searching the Knowledge Base\nTo perform a semantic search within your knowledge base, use the search command along with your prompt:\n\n```shell\nhive search "your prompt"\n```\nHive will analyze your prompt and match it against the indexed content, providing you with the most relevant results based on semantic similarity.\n\n#### Example Search Output\nHere\'s an example output of a search performed with Hive:\n\n```shell\nhive search "are honey bees good?"              \n\n╭─ ./data/the-problem-with-honey-bees.md ──────────────────────────────────────────────────────────────────────────────╮\n│                                                                                                                      │\n│  But think about them, we must. I used to believe that honey bees were a gateway species, and that concern over      │\n│  their health and prosperity would spill over onto native bees, benefitting them, too. While this may have happened  │\n│  in some cases, evidence is mounting that misguided enthusiasm for honey bees has likely been to the native bees’    │\n│  detriment. Beekeeping doesn’t make me feel good, anymore. In fact, quite the opposite.                              │\n│                                                                                                                      │\n╰─ Match score: 73% ───────────────────────────────────────────────────────────────────────────────────────────────────╯\n```\nThe search output displays the matched file, along with the relevant text snippet and a match score indicating the similarity between the prompt and the content.\n\n🔍 Hive makes it easy to find the information you need, saving you time and effort!\n\n## Contributing\nWe welcome contributions to Hive! Feel free to open issues and submit pull requests for any enhancements or bug fixes. Let\'s make Hive even better together! 🚀\n\n## License\nHive is licensed under the MIT License.\n\n🐝 Don\'t waste time searching, let Hive be your knowledge navigator! Start exploring your knowledge base effortlessly with Hive. Happy searching! 🚀✨',
    'author': 'paul',
    'author_email': 'ppierzc@gmail.copm',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<3.12',
}


setup(**setup_kwargs)
