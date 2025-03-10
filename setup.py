from setuptools import setup
from h9web._version import __version__ as version


setup(
    name='h9web',
    version=version,
    description='Web based h9 client',
    author='Kamil Palkowski',
    author_email='sq8kfh@gmail.com',
    url='https://github.com/sq8kfh/h9web',
    packages=['h9web'],
    include_package_data=True,
    classifiers=[
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    python_requires='>=3.7',
    install_requires=[
        'tornado>=6.4.2',
        'python-dateutil>=2.9.0.post0'
    ],
)
