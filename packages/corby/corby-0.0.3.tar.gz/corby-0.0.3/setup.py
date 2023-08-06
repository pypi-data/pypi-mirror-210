from setuptools import setup, find_packages

python_requires='>=3.6',

setup(
    name="corby",
    version="0.0.3",
    description="⚡ Create your LLMs applications from zero to deploy in minutes ⚡",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Jose Hervás Díaz",
    author_email='jhervasdiaz@gmail.com',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        "inquirer",
        "jinja2",
        "gitpython",
    ],
)
