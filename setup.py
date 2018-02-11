#!/usr/bin/env python3

from setuptools import setup

requirements = [
    'pulpcore-plugin',
]

setup(
    name='pulp-nupkg',
    version='0.0.1a1.dev1',
    description='pulp-nupkg plugin for the Pulp Project',
    author='AUTHOR',
    author_email='author@email.here',
    url='http://example.com/',
    install_requires=requirements,
    include_package_data=True,
    packages=['pulp_nupkg', 'pulp_nupkg.app'],
    entry_points={
        'pulpcore.plugin': [
            'pulp_nupkg = pulp_nupkg:default_app_config',
        ]
    }
)
