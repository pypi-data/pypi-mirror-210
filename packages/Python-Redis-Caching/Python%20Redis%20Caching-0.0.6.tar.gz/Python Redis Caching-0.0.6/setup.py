from setuptools import setup

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='Python Redis Caching',
    version='0.0.6',
    author='Hoang Nguyen',
    author_email='minhhoangnguyenbao99@gmail.com',
    description='Caching your data to Redis',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/nbmhoang/python-redis-caching',
    install_requires=[
        'redis'
    ],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)