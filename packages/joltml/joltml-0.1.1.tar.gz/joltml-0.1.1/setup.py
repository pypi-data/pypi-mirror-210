from setuptools import setup, find_packages
from pathlib import Path

here = Path(__file__).resolve().parent
README = (here / "README.md").read_text(encoding="utf-8")
VERSION = (here / 'joltml' / "VERSION").read_text(encoding="utf-8").strip()

setup(
    name='joltml',
    packages=['joltml',
              ] + find_packages(exclude=['tests', 'tests.*']),
    include_package_data=True,
    entry_points={
        "console_scripts": ["joltml=joltml.cli:execute_cli"],
    },
    version=VERSION,
    license='mit',
    description='joltml unravels the dark side of machine learning models',
    long_description=README,
    long_description_content_type='text/markdown',
    author='Sherif Abdulkader Tawfik Abbas',
    author_email='sherif.tawfic@gmail.com',
    url='https://github.com/sheriftawfikabbas/joltml',
    keywords=['ai', 'machine learning', 'machine learning workflow'
              'model tracking'],
    install_requires=['xgboost',
                      'pandas',
                      'numpy',
                      'torch',
                      'tensorflow',
                      'sklearn'],

)
