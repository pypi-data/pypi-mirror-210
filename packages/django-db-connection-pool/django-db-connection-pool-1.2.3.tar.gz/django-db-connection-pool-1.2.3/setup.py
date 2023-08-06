# encoding: utf-8

import codecs
import shutil
import setuptools

from dj_db_conn_pool import (
    __version__,
    __author__,
    __author_email__,
    __description__
)


def clean(name):
    def decorator(func):
        def smash_the_egg():
            shutil.rmtree(name + '.egg-info', ignore_errors=True)
        return lambda: [fn() for fn in [smash_the_egg, func, smash_the_egg]]
    return decorator


@clean('django_db_connection_pool')
def setup():
    setuptools.setup(
        name='django-db-connection-pool',
        license='MIT',
        version=__version__,
        description=__description__,
        long_description=codecs.open('README.md', encoding='UTF-8').read(),
        long_description_content_type='text/markdown',
        author=__author__,
        author_email=__author_email__,
        url='https://github.com/altairbow/django-db-connection-pool',
        download_url='https://pypi.python.org/pypi/django-db-connection-pool/',
        packages=setuptools.find_packages(),
        include_package_data=True,
        install_requires=[
            'Django>=2.0',
            'SQLAlchemy>=1.4.24',
            'sqlparams>=4.0.0',
        ],
        extras_require={
            'all': [
                'JPype1>=1.3.0',
                'sqlparams>=3.0.0',
                'PyMySQL>=0.9.3',
                'pyodbc>=4.0.34',
                'cx-Oracle>=6.4.1',
                'psycopg2>=2.8.6',
            ],
            'jdbc': ['JPype1>=1.3.0'],
            'mysql': ['PyMySQL>=0.9.3'],
            'odbc': ['pyodbc>=4.0.34'],
            'oracle': ['cx-Oracle>=6.4.1'],
            'postgresql': ['psycopg2>=2.8.6'],
        },
        classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Environment :: Web Environment',
            'Framework :: Django',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Operating System :: OS Independent',
            'Programming Language :: Python :: 3',
            'Topic :: Software Development :: Libraries :: Python Modules',
        ],
        keywords=['django', 'db', 'database', 'persistent', 'connection', 'pool', 'pooling'],
    )


if __name__ == '__main__':
    setup()
