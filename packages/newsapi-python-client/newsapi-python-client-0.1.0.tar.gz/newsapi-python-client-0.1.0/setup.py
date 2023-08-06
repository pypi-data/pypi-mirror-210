from setuptools import setup, find_packages

setup(
    name='newsapi-python-client',
    version='0.1.0',
    url='https://github.com/roachseb/NewsAPI-Python-Client',
    author='Roach Sebastien',
    author_email='sebastien.r.r@hotmail.com',
    description='Python client for the NewsAPI.org API',
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
)
