import pathlib
from setuptools import setup, find_packages

HERE = pathlib.Path(__file__).parent

VERSION = '0.1.5'
PACKAGE_NAME = 'gensum'
AUTHOR = 'Aaron Briel'
AUTHOR_EMAIL = 'aaronbriel@gmail.com'
URL = 'https://github.com/aaronbriel/gensum'

LICENSE = 'Apache License 2.0'
DESCRIPTION = 'Generative Summarization for Data Augmentation'
LONG_DESCRIPTION = (HERE / "README.md").read_text()
LONG_DESC_TYPE = "text/markdown"

INSTALL_REQUIRES = [
    'numpy',
    'pandas',
    'openai'
]

setup(name=PACKAGE_NAME,
      version=VERSION,
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      long_description_content_type=LONG_DESC_TYPE,
      author=AUTHOR,
      license=LICENSE,
      author_email=AUTHOR_EMAIL,
      url=URL,
      install_requires=INSTALL_REQUIRES,
      packages=find_packages()
      )