from setuptools import setup
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='error_suggester',
    version='0.1.1',
    url='https://github.com/HarisBinSaif/ErrorSuggester',
    project_urls={
        'GitHub': 'https://github.com/HarisBinSaif/ErrorSuggester',
    },
    description='A Python library for error suggestions using ChatGPT',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='HarisBinSaif',
    packages=['error_suggester'],
    install_requires=[
        'openai',
        # Add other dependencies here if necessary
    ],
)
