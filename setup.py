# -*- coding: utf-8 -*-

from setuptools import find_packages, setup


def requirements(filename):
    """Reads requirements from a file."""
    with open(filename) as f:
        return [x.strip() for x in f.readlines() if x.strip()]


setup(name='koach',
      version='1.0',
      description='korean grammer checker',
      author='Chanwoong Kim',
      author_email='me@chanwoong.kim',
      url='',
      packages=find_packages(),
      entry_points={
          'console_scripts': ['koach = koach.__main__:cli']
      },
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'License :: OSI Approved :: MIT License',
          'Natural Language :: Korean',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Topic :: Utilities',
      ],
      install_requires=requirements('requirements.txt'),
      # test_require=requirements('test/requirements.txt'),
      )
