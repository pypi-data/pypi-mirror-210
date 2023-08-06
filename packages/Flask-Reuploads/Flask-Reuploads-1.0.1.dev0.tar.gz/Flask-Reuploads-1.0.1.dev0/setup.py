import codecs
import os

from setuptools import find_packages
from setuptools import setup

HERE = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    """Return the contents of the read file.

    - Build an absolute path from *parts*
    - Return the contents of the resulting file.
    - Assume UTF-8 encoding.

    Proudly copy-pasted from Hynek's attrs project
    (minus the typo).

    Simply renamed Jürgen Gmach's Flask-Reuploaded
    project.

    CopyCat: Subrata Sarker <picklumithu@yahoo.com>
    """
    with codecs.open(os.path.join(HERE, *parts), "rb", "utf-8") as f:
        return f.read()


LONG = read("README.rst") + "\n\n" + read("CHANGES.rst")

setup(
    name="Flask-Reuploads",
    version="1.0.1.dev0",
    url="https://github.com/picklu/flask-reuploads",
    project_urls={
        "Source": "https://github.com/picklu/flask-reuploads",
        "Issue Tracker": "https://github.com/jugmac00/flask-reuploaded/issues",
        "Documentation": "https://flask-reuploaded.readthedocs.io/en/latest/",
    },
    license="MIT",
    author='Matthew "LeafStorm" Frazier',
    author_email="leafstormrush@gmail.com",
    maintainer="Jürgen Gmach, Subrata Sarker",
    maintainer_email="juergen.gmach@googlemail.com, picklumithu@yahoo.com",
    description="Flexible and efficient upload handling for Flask",
    long_description=LONG,
    long_description_content_type="text/x-rst",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    zip_safe=False,
    platforms="any",
    include_package_data=True,
    install_requires=["Flask>=1.0.4"],
    extras_require={
        "test": [
            "pytest",
            "pytest-cov",
        ],
    },
    python_requires=">= 3.7",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Framework :: Flask",
    ],
)
