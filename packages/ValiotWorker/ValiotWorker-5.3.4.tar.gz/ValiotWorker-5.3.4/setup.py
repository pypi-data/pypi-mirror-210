#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

# reference: https://stackoverflow.com/questions/458550/standard-way-to-embed-version-into-python-package#:~:text=should%20be%20placed%20after%20the,previous%20version%20of%20this%20standard).&text=It%20should%20be%20a%20string,version_info%20for%20the%20tuple%20version.


def get_package_version(version_file):
    import re
    verstrline = open(version_file, "rt").read()
    VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
    mo = re.search(VSRE, verstrline, re.M)
    if mo:
        verstr = mo.group(1)
        return verstr
    else:
        raise RuntimeError(
            "Unable to find version string in %s." % (version_file,))


__version__ = get_package_version("ValiotWorker/__version__.py")

requirements = [
    # TODO: put package requirements here
    'colorama>=0.4, <0.5',
    'croniter>=1.3, <2.0',
    'pydash>=5.0, <6.0',
    'pygqlc>=3.0.1, <4.0.0',
    'python-dateutil>=2.8.2, <3.0',
    'pytz==2022.2.1',
    'redis>=4.3.4, <5.0',
    'singleton-decorator>=1.0, <2.0',
    'termcolor>=2.0.1, <3.0',
    'tzlocal>=4.2, <5.0',
    'velebit-useful-logs>=1.0, <2.0'

]

setup_requirements = [
    # TODO(alanbato): put setup requirements (distutils extensions, etc.) here
    'twine',
]

test_requirements = [
    # TODO: put package test requirements here
    'pytest',
    'pytest-cov',
    'pylint',
]

desc = "Enables running Python functions as standalone jobs based on interaction with valiot-jobs API"
with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='ValiotWorker',
    version=__version__,
    description=desc,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author="Valiot",
    author_email="hiring@valiot.io",
    url='https://github.com/valiot/python-gql-worker',
    packages=find_packages(include=['ValiotWorker']),
    entry_points={
        'console_scripts': [
            'ValiotWorker=ValiotWorker.__main__:main'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    zip_safe=False,
    keywords='ValiotWorker',
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
)
