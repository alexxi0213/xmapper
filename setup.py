from setuptools import find_packages
from setuptools import setup

version = '1.0.0'

with open('requirements.txt') as f:
    requires = f.read().strip().split('\n')


setup(
    name="xmapper",
    version=version,
    description='xml mapper',
    long_description=open('README.md').read(),
    author='Alex xi',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
)
