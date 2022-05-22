from __future__ import print_function
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import codecs
import os
import sys
import re

here = os.path.abspath(os.path.dirname(__file__))

def read(*parts):
    # intentionally *not* adding an encoding option to open
    return codecs.open(os.path.join(here, *parts), 'r').read()

def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

long_description = read('README.rst')

class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ['--strict', '--verbose', '--tb=long', 'tests']
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)

setup(
    name='coned',
    version=find_version('coned', '__init__.py'),
    url='https://github.com/bvlaicu/coned/',
    license='Apache Software License',
    author='Bogdan Vlaicu',
    tests_require=['pytest'],
    install_requires=['requests', 'pyppeteer', 'pyotp'],
    cmdclass={'test': PyTest},
    author_email='bogdanvlaicu@yahoo.com',
    description='Python client for ConEdison smart energy meters',
    long_description=long_description,
    entry_points={
        'console_scripts': [
            'conedctl = coned.conedctl:run',
            ],
        },
    packages=['coned'],
    include_package_data=True,
    platforms='any',
    test_suite='coned.test.test_coned',
    zip_safe=False,
    package_data={'coned': ['templates/**', 'static/*/*']},
    classifiers = [
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Development Status :: 4 - Beta',
        'Natural Language :: English',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        ],
    extras_require={
        'testing': ['pytest'],
      }
)
