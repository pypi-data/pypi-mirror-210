import pathlib
from setuptools import setup, find_packages

HERE = pathlib.Path(__file__).parent
VERSION = '1.0.0'
PACKAGE_NAME = 'akasa'
AUTHOR = 'Bijay Das'
AUTHOR_EMAIL = 'imbijaydas@gmail.com'

LICENSE = 'GNU GENERAL PUBLIC LICENSE'
DESCRIPTION = 'This is a cool package'
LONG_DESCRIPTION = open('README.md', 'r').read()
LONG_DESC_TYPE = 'text/markdown'

setup(name=PACKAGE_NAME,
      version=VERSION,
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      long_description_content_type=LONG_DESC_TYPE,
      author=AUTHOR,
      license=LICENSE,
      author_email=AUTHOR_EMAIL,
      packages=find_packages()
      )
