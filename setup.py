from pip._internal.download import PipSession
from pip._internal.req import parse_requirements
from setuptools import setup
from setuptools import find_packages

version = '1.0.0'

install_reqs = parse_requirements('./requirements.txt', session=PipSession())
requires = [str(ir.req) for ir in install_reqs]

setup(
    name="mytangle",
    version=version,
    description='mytangle,
    long_description=open('README.md').read(),
    author='Alex xi',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
)
