"""
Setup the plugin
"""
from setuptools import setup, find_packages

setup(
    name='mkdocs-simple-tags-plugin',
    version='0.5',
    python_requires='>=3.8',
    install_requires=[
        'mkdocs>=1.4.3',
    ],
    packages=find_packages(exclude=['*.tests']),
    package_data={'tags': ['templates/*.md.template']},
    entry_points={
        'mkdocs.plugins': [
            'simple-tags = tags.plugin:TagsPlugin'
        ]
    }
)
