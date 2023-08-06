from setuptools import setup, find_packages

# Read the contents of the README file
with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='DataDoctor',
    version='1.0.3',
    author='Aryan Bajaj',
    author_email='aryanbajaj104@email.com',
    description="A Python package for data cleaning and preprocessing.",
    long_description=long_description,
    long_description_content_type='text/markdown',
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