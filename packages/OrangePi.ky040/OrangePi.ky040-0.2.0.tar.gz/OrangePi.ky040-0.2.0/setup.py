from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='OrangePi.ky040',
    version='0.2.0',
    description='High-level interface for the KY040 rotary encoder and switch.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/sonocotta/orangepi-ky040',
    author='Andriy Malyshenko',
    author_email='anriy@sonocotta.com',
    keywords='keyes rotary encoder switch ky040',
    packages=find_packages(),
    install_requires=['OPi.GPIO'],
    extras_require={
        "device": ["evdev"]
    },
    project_urls={
        'Bug Reports': 'https://github.com/sonocotta/orangepi-ky040/issues',
        'Source': 'https://github.com/sonocotta/orangepi-ky040',
    },
)
