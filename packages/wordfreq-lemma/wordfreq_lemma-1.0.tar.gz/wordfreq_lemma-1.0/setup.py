#!/usr/bin/env python

from distutils.core import setup

setup(name='wordfreq_lemma',
      version='1.0',
      description='Lemmatized Word Frequency',
      author='Hao Wu',
      author_email='haowu@dataset.sh',
      url='',
      packages=['wordfreq_lemma'],
      package_data={'mypkg': ['data/*.dat']},
      requires=['nltk']
      )
