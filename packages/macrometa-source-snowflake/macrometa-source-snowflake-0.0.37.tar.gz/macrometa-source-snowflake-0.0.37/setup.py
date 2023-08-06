#!/usr/bin/env python

from setuptools import setup

with open('README.md') as f:
    long_description = f.read()

setup(name='macrometa-source-snowflake',
      version='0.0.37',
      description='Macrometa Source for extracting data from Snowflake',
      long_description=long_description,
      long_description_content_type='text/markdown',
      author="Macrometa",
      url='https://github.com/Macrometacorp/macrometa-source-snowflake',
      classifiers=[
          'License :: OSI Approved :: Apache Software License',
          'Programming Language :: Python :: 3 :: Only'
      ],
      py_modules=['macrometa_source_snowflake'],
      install_requires=[
          'pipelinewise-singer-python==1.2.0',
          'snowflake-connector-python[pandas]==2.7.*',
          'pendulum==1.2.0',
          'c8connector>=0.0.20'
      ],
      extras_require={
          'test': [
              'pylint==2.12.*',
              'pytest==7.0.1',
              'pytest-cov==4.0.0',
              'unify==0.5'
          ]
      },
      entry_points='''
          [console_scripts]
          macrometa-source-snowflake=macrometa_source_snowflake:main
      ''',
      packages=['macrometa_source_snowflake',
                'macrometa_source_snowflake.sync_strategies'],
      )
