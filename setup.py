import os
from setuptools import setup

# Read the version without importing h9web - the project dir isn't on sys.path in isolated (PEP 517) builds
_version = {}
with open(os.path.join(os.path.dirname(__file__), 'h9web', '_version.py')) as f:
    exec(f.read(), _version)
version = _version['__version__']


setup(
    name='h9web',
    version=version,
    description='Web based h9 client',
    author='Kamil Palkowski',
    author_email='sq8kfh@gmail.com',
    url='https://github.com/sq8kfh/h9web',
    # h9 and jsonrpc are vendored next to h9web and imported by it (h9.msg is not used)
    packages=['h9web', 'h9', 'h9.asyncmsgstream', 'jsonrpc'],
    include_package_data=True,
    classifiers=[
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
    ],
    python_requires='>=3.9',
    install_requires=[
        'tornado>=6.5',
    ],
    entry_points={
        'console_scripts': [
            'h9web = h9web.main:main',
        ],
    },
)
