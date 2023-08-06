#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# yfinance-extended - extending yfinance
# https://github.com/zhaohan-dong/yfinance-extended

"""yfinance-extended"""

from setuptools import setup

from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='yfinance-extended',
    version="0.0.3",
    description='Extension of yfinance package to download wide-form stock data from Yahoo! Finance',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/zhaohan-dong/yfinance-extended',
    author='Zhaohan Dong',
    author_email='zhaohan_dong@yahoo.com',
    license='bsd-3-clause',
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Development Status :: 3 - Alpha',
        # 'Development Status :: 4 - Beta',
        # 'Development Status :: 5 - Production/Stable',

        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Topic :: Office/Business :: Financial',
        'Topic :: Office/Business :: Financial :: Investment',
        'Topic :: Scientific/Engineering :: Interface Engine/Protocol Translator',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',

        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11'
    ],
    platforms=['any'],
    install_requires=['yfinance>=0.2.18', 'pyarrow>=12.0.0']
)
