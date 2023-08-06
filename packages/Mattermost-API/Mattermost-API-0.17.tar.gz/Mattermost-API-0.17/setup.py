#!/usr/bin/env python3

from setuptools import setup, find_packages

with open('README.md') as readme_file:
    README = readme_file.read()

with open('HISTORY.md') as history_file:
    HISTORY = history_file.read()

setup_args = dict(
    name='Mattermost-API',
    version='0.17',
    description='Simple Mattermost API library',
    long_description_content_type="text/markdown",
    long_description=README + '\n\n' + HISTORY,
    license='MIT',
    packages=find_packages(),
    author='Aleksandr Kuznetsov, Aleksandr Zarin',
    author_email='izhatomic@yandex.ru, vector-777@yandex.ru',
    keywords=['mattermost', 'mattermostapi', 'mattermost-api', "mattermost api", "mm api", "mm-api"],
    url='https://github.com/izhatomic/mattermost-api',
    download_url='https://pypi.org/project/mattermost-api/'
)

install_requires = [
    'requests'
]

if __name__ == '__main__':
    setup(**setup_args, install_requires=install_requires)
