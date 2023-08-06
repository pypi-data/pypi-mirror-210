from setuptools import setup, find_packages
import codecs
import os

def read_file(path):
    with open(path) as contents:
        return contents.read()

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.1.0'
DESCRIPTION = 'Flask based notebook for personal and research projects.'
LONG_DESCRIPTION = 'A Flask-based notebook for managing and sharing personal and research projects.'

# Setting up
setup(
    name="fresnote",
    version=VERSION,
    author="Dimitrios Kioroglou",
    author_email="<d.kioroglou@hotmail.com>",
    license="CC-BY-NC-SA-4.0",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    keywords=["flask", "notebook", "research", "reporting"],
    install_requires=read_file("requirements.txt"),
    packages=find_packages(),
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ],
    package_data={
        "fresnote": [
            "static/css/*",
            "static/js/*",
            "static/icons/*",
            "static/gojssrc/*",
            "static/tablegrid/*",
            "templates/*"
        ]
    },
    entry_points={
        "console_scripts": [
            "fresnote = fresnote.cli.script:main"
        ]
    },
    zip_safe=False,
)
