from setuptools import setup


with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='json2csv',
    version='0.0.1',
    description='Library for converting JSON to CSV',
    author='Ed',
    author_email='agabsed@gmail.com',
    packages=['json2csv'],
    install_requires=[],
)
