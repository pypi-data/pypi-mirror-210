import os
from setuptools import setup, find_packages

# Read the contents of your README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='newsapi-python-client',
    version='0.2.2',
    url='https://github.com/roachseb/NewsAPI-Python-Client',
    author='Roach Sebastien',
    author_email='sebastien.r.r@hotmail.com',
    packages=find_packages(exclude=['tests*']),
    install_requires=[
        'requests',
        'dataclasses;python_version<"3.7"'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    license='MIT',
    description='A Python client to interact with News API from NewApi.org',
    long_description=long_description,
    long_description_content_type='text/markdown'

)
