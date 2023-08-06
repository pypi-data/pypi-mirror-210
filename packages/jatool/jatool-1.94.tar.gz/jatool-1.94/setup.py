from setuptools import setup, find_packages
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='jatool',
    version='1.94',
    author='Pigpig',
    author_email='21310238@tongji.edu.cn',
    description='A Python package for jatools',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bigbrolv/jatool",
    packages=find_packages(),
    classifiers=[
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    ],
    install_requires=[
        'pandas',
        'ginza',
        'chardet',
        'ja_ginza',
        'gensim',
        'matplotlib',
        'scikit-learn',
        'seaborn',
        'transformers',
        'torch',
        'tensorflow',
        'xformers',
        'fugashi',
        'xformers',
        'ipadic'
    ],
)