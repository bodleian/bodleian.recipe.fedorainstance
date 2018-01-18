# -*- coding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup
import os
import sys

version = open(
    os.path.join("bodleian", "recipe", "fedora", "version.txt",)
).read().strip()


def read(name):
    return open(os.path.join(os.path.dirname(__file__), name)).read()


requires = ['setuptools', 'hexagonit.recipe.download']

if sys.version_info >= (3,):
    requires += [
        'zc.buildout>=2.0.0a1',
        ]
else:
    requires += [
        'zc.buildout',
        ]

test_requires = [
    'nose',
    'nose-cov',
    'rednose',
    'mock'    
]

long_description = '\n'.join([
    read('README.rst')
])


setup(
    name='bodleian.recipe.fedora',
    version=version,
    description="zc.buildout to configure a fedora instance",
    long_description=long_description,
    classifiers=[
        'Framework :: Buildout',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: Build Tools',
    ],
    keywords='',
    author='CB',
    author_email='github@bodleian.ox.ac.uk',
    url='http://pypi.python.org/pypi/bodleian.recipe.fedora',
    license='MIT',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['bodleian', 'bodleian.recipe'],
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
    extras_require={
        'test' : test_requires,
    },
    # TODO: Make multicore the default behavior in next major releases
    # since its solr default setup since 5.0.0
    entry_points={
        "zc.buildout": [
            "default = bodleian.recipe.fedora:FedoraRecipe"
        ]
    },
)
