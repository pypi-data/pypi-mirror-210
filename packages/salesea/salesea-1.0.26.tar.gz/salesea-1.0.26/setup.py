# -*- coding: utf-8 -*-
from io import open
from setuptools import setup, find_packages

# ------------------------------------------------------------------------------- #

with open('README.md', 'r', encoding='utf-8') as fp:
    readme = fp.read()

# with open("requirements.txt", "r", encoding="utf8") as f:
#     requires = f.read()
#     print(requires.splitlines())
# ------------------------------------------------------------------------------- #

setup(
    name='salesea',
    author='howard',
    author_email='18071131140telephone@gmail.com',
    version='1.0.26',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    description='This is an Nginx log collection tool.',
    long_description=readme,
    long_description_content_type='text/markdown',
    keywords=[
        'nginx',
        'logs',
        'collection'
    ],
    # package_data={'': ['*.*']},
    # install_requires=['aiohttp>=3.8.4',
    #                   'aiosignal>=1.2.0',
    #                   'async-timeout>=4.0.2',
    #                   'attrs>=21.4.0',
    #                   'charset-normalizer>=2.0.7',
    #                   'frozenlist>=1.2.0',
    #                   'idna>=3.3',
    #                   'multidict>=5.2.0',
    #                   'yarl>=1.7.2'],
    install_requires=[
        'requests>=2.18.4',
        ''
    ],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.0',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    entry_points={'console_scripts': "salesea = salesea.__main__:main"},
    python_requires='>=3.0',
)

# ------------------------------------------------------------------------------- #
