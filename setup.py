from setuptools import setup, find_packages

setup(
    name="IArena",
    author="jparisu",
    author_email="javier.paris.u@gmail.com",
    url="https://github.com/jparisu/IArena",
    version="0.0",
    package_dir={'': 'src'},
    packages=find_packages(where='src')
)
