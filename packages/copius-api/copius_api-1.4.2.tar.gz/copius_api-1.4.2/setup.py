"""
Setup-Script for loanpy
"""

from setuptools import setup, find_packages
from pathlib import Path

setup(
  name='copius_api',
  description='Transcription & orthography toolset',
  long_description=open("README.rst").read(),
  author='Viktor Martinović',
  author_email='viktoringermany@gmail.com',
  version='1.4.2',
  packages=find_packages(),
  extras_require={
  "test": ["pytest>=7.1.2"],
  "dev": ["wheel", "twine", "sphinx"]
  },
  install_requires=[
          'requests',
          'beautifulsoup4',
      ],
  keywords=['linguistics', 'transcription'],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Science/Research',
    'Topic :: Scientific/Engineering',
    "Topic :: Text Processing :: Linguistic",
    'License :: OSI Approved :: MIT License',
    'Natural Language :: English',
    'Operating System :: POSIX :: Linux',
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",

  ],
  url='https://github.com/martino-vic/copius_api',
  download_url='https://github.com/martino-vic/copius_api/archive/refs/tags/v1.4.2.tar.gz',
  license='MIT',
  platforms=["Linux"],
  python_requires=">=3.7",
  project_urls={
  "continuous integration": "https://app.circleci.com/pipelines/github/martino-vic/copius_api?branch=master",
  }
)
