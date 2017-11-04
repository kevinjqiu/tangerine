import setuptools
import json


def get_install_requires():
    with open('Pipfile.lock') as f:
        piplock = json.load(f)
    return [
        '{}{}'.format(dep, details['version'])
        for dep, details in piplock['default'].items()
    ]


setuptools.setup(
    name="tangerine",
    version=open('tangerine/VERSION').read(),
    url="https://github.com/kevinjqiu/tangerine",

    author="Kevin J. Qiu",
    author_email="kevin@idempotent.ca",

    description="API for the Tangerine Bank",
    long_description=open('README.md').read(),

    include_package_data=True,

    packages=setuptools.find_packages(),

    install_requires=get_install_requires(),

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
