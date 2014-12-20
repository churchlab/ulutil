from glob import glob

from setuptools import setup, find_packages

def readme():
    with open('README.md', 'r') as ip:
        return ip.read()

setup(
    name='ulutil',
    version='0.1.0',
    description='Python utilities for Church lab work (mostly DNA sequencing)',
    long_description=readme(),
    author='Uri Laserson',
    author_email='uri.laserson@gmail.com',
    url='https://github.com/churchlab/ulutil',
    packages=find_packages(),
    scripts=glob('bin/*.py'),
    keywords=('python sequencing dna lsf sanger streamgraph oligos primers'),
    license='Apache License, Version 2.0',
    classifiers=[
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7'
    ],
    zip_safe=True
)
