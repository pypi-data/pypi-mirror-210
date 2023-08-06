from pathlib import Path

from setuptools import setup

setup(
    name='python_mop',
    version='0.0.1',
    packages=['mop'],
    url='https://github.com/CDU-Ge/python_mop',
    license='MIT LICENSE',
    author='CDU-Ge',
    author_email='cosplox@outlook.com',
    description='python toolkit for monitor-oriented programming.',
    long_description=Path("README.md").read_text(encoding='utf8'),
    long_description_content_type="text/markdown"

)
