from setuptools import setup, find_packages

# Read requirements from requirements.txt
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name="IArena",
    description="Framework to build AIs to play games",
    author="jparisu",
    author_email="javier.paris.u@gmail.com",
    url="https://github.com/jparisu/IArena",
    version="0.0",
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    install_requires=requirements,
)
