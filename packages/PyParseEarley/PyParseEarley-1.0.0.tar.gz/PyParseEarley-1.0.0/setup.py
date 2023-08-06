from setuptools import setup, find_packages
from os import path as os_path

this_directory = os_path.abspath(os_path.dirname(__file__))


def read_file(filename):
    with open(os_path.join(this_directory, filename), encoding='utf-8') as f:
        long_description = f.read()
    return long_description


def read_requirements(filename):
    return [line.strip() for line in read_file(filename).splitlines()
            if not line.startswith('#')]


setup(name='PyParseEarley',
      python_requires='>=3.5',
      version='1.0.0',
      description='Yet Another Earley Parser: Efficient parsing algorithm for context-free grammars.',
      long_description=read_file('README.md'),
      long_description_content_type="text/markdown",
      url='https://github.com/t3bol90/YAEP',
      author='Toan Doan',
      author_email='toandd.i81@gmail.com',
      license='MIT',
      packages=find_packages(),
      platforms=['linux', 'windows', 'macos'],
      install_requires=['pydot', 'cairosvg'],
      zip_safe=False)