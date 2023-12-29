import re
from setuptools import setup, find_packages


def readme():
    """Return the contents of the project README file."""

    with open('README.md') as f:
        return f.read()


version = re.search(r"__version__ = ['\"]([^'\"]*)['\"]", open('glory/__init__.py').read(), re.M).group(1)

setup(
    name='glory',
    version=version,
    packages=find_packages(),
    url='https://github.com/JGCRI/glory',
    license='BSD-2-Clause',
    author='Mengqi Zhao',
    author_email='mengqi.zhao@pnnl.gov',
    description='A python package for the Global Reservoir Yield (GLORY) model.',
    long_description=readme(),
    long_description_content_type="text/markdown",
    python_requires='>=3.5, <4',
    include_package_data=True,
    install_requires=[
        "pytest",
        "tqdm",
        "requests",
        "pandas>1.5",
        "numpy>=1.23",
        "PyYAML>=6",
    ],
    extras_require={
        'dev': [
            "pytest",
            "autodoc>=0.5.0",
            "twine>=4.0.1",
            "ipykernel>=6.15.1",
            "sphinx>=4.0.2",
            'sphinx-panels>=0.6.0',
            'sphinx-rtd-theme>=0.5.2',
            'sphinx-mathjax-offline>=0.0.1'
        ]
    }
)
