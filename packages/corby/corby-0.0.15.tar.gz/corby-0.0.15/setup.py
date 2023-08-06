'''Pypi setup file for corby'''

from setuptools import setup, find_packages

setup(
    name="corby",
    version="0.0.15",
    description="⚡ Create your LLMs applications from zero to deploy in minutes ⚡",
    # pylint: disable=consider-using-with
    long_description=open("README.md", encoding='utf-8').read(),
    long_description_content_type="text/markdown",
    author="Jose Hervás Díaz",
    author_email='jhervasdiaz@gmail.com',
    license='MIT',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'corby = corby.__main__:main',
        ],
    },
    install_requires=[
        "inquirer",
        "jinja2",
        "gitpython",
    ],
)
