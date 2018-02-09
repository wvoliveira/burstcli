from codecs import open
from os.path import abspath, dirname, join
from subprocess import call
from setuptools import Command, find_packages, setup
from burst import __version__

this_dir = abspath(dirname(__file__))
with open(join(this_dir, 'README.md'), encoding='utf-8') as file:
    long_description = file.read()


class RunTests(Command):
    description = 'run tests'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    @staticmethod
    def run():
        error = call(['py.test', '--cov=burstcli', '--cov-report=term-missing'])
        raise SystemExit(error)


setup(
    name='burst',
    version=__version__,
    description='Open some tickets in one time at GLPI',
    long_description=long_description,
    url='https://github.com/wvoliveira/burstcli',
    author='Wellington Oliveira',
    author_email='oliveira@live.it',
    license='MIT',
    classifiers=[
        'Intended Audience :: Developers',
        'Topic :: Utilities',
        'License :: MIT',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='cli glpi burst',
    packages=find_packages('.', exclude=['docs', 'tests*']),
    package_data={'burst': ['conf/example.ini']},
    install_requires=['pymysql', 'tabulate', 'ldap3'],
    extras_require={'test': ['coverage', 'pytest', 'pytest-cov']},
    entry_points={'console_scripts': ['burst=burst.cli:main']},
    cmdclass={'test': RunTests},
)
