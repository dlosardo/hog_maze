#!/usr/bin/env python3

from setuptools import setup
from os import path


def get_requirements():
    """Reads the installation requirements from requirements.pip"""
    with open("requirements.pip") as f:
        lines = f.read().split("\n")
        requirements = list(filter(lambda l: not l.startswith('#'), lines))
        return requirements


here = path.abspath(path.dirname(__file__))

setup(name='hog_maze',
      description='Hog Maze Game',
      long_description='',
      author='Diane Losardo',
      url='todo',
      download_url='todo',
      author_email='dlosardo@gmail.com',
      version='0.1',
      install_requires=get_requirements(),
      packages=['hog_maze', 'hog_maze/components',
                'hog_maze/util', 'hog_maze/states',
                'hog_maze/debug', 'hog_maze/maze',
                'hog_maze/game_states'
                ],
      package_dir={'hog_maze': 'hog_maze'},
      scripts=['hog_maze/hoggy.py'],
      include_package_data=True
      )
