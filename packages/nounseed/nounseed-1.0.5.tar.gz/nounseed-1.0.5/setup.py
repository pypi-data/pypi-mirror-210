from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='nounseed',
    version='1.0.5',
    description='A package for generating and storing project ideas',
    author='psibir',
    packages=['nounseed'],
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
        'argparse',
        'Pathlib'
    ],
    entry_points={
        'console_scripts': [
            'nounseed = nounseed.__main__:main'
        ]
    }
)
