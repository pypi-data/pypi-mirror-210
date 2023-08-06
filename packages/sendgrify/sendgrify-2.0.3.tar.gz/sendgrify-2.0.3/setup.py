# read the contents of your README file
from pathlib import Path

from setuptools import setup

this_directory = Path(__file__).parent
long_description = (this_directory / 'README.md').read_text()

REQUIREMENTS = (
    'sendgrid==5.3.0',
    'markdown',
)

setup(
    name='sendgrify',
    version='2.0.3',
    url='https://github.com/sdelquin/sendgrify.git',
    author='Sergio Delgado Quintero',
    author_email='sdelquin@gmail.com',
    description='SendGrid for Humans',
    license='MIT',
    packages=['sendgrify'],
    install_requires=REQUIREMENTS,
    long_description=long_description,
    long_description_content_type='text/markdown',
)
