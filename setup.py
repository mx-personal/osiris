from distutils.core import setup
from setuptools import find_packages
setup(
  name='osiris',
  version='0.5',      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description='Emulator for real life rhythm',   # Give a short description about your library
  author='mx-personal',                   # Type in your name
  url='https://github.com/mx-personal/osiris',   # Provide either the link to your github or to your website
  keywords=['osiris'],   # Keywords that define your package best
  include_package_data=True,
  packages=find_packages(),   # Chose the same as "name"
  package_data={'osiris': ['*.txt', '*.csv']},
)