# pylint: disable=missing-module-docstring

from setuptools import find_packages, setup

with open('README.md', encoding='utf-8') as f:
  readme = f.read()

setup(
  name = 'i18nx',
  version = '1.3.0',
  description = "Lightweight i18n for Python",
  long_description = readme,
  long_description_content_type = 'text/markdown',
  keywords = 'i18n internationalization translate',
  readme = 'README.md',
  python_requires = '>=3.9',
  license = 'MIT',
  packages = find_packages(exclude = ['tests/*']),
  author = 'Sébastien Demanou',
  author_email = 'demsking@gmail.com',
  url = 'https://gitlab.com/demsking/i18nx',
  install_requires = [],
  project_urls={
    'Documentation': 'https://gitlab.com/demsking/i18nx/-/blob/main/README.md',
    'Say Thanks!': 'https://www.buymeacoffee.com/demsking',
    'Source': 'https://gitlab.com/demsking/i18nx',
    'Tracker': 'https://gitlab.com/demsking/i18nx/-/issues',
  },
  classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Software Development :: Localization',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3.9',
  ],
)
