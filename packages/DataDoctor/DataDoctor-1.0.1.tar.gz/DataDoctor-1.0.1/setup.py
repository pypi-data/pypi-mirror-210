from setuptools import setup, find_packages

setup(
    name='DataDoctor',
    version='1.0.1',
    author='Aryan Bajaj',
    author_email='aryanbajaj104@email.com',
    description="A Python package for data cleaning and preprocessing.",
    packages=find_packages(),
    install_requires=[
        'pandas',
        'numpy',
        'scikit-learn',
        'fuzzywuzzy',
        'python-Levenshtein',
        'chardet'
    ],
)