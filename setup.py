import pathlib

from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(
    name="docstring_generator",
    version="0.2.0",
    packages=[
        "docstring_generator",
    ],
    url="https://github.com/FelixTheC/docstring_generator",
    license="MIT",
    author="FelixTheC",
    author_email="felixeisenmenger@gmx.net",
    description="Generate Docstrings with type-hint informations",
    long_description=README,
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Topic :: Utilities",
        "Topic :: Software Development :: Documentation",
        "Typing :: Typed",
    ],
    python_requires=">=3.9",
    install_requires=["click", "strongtyping"],
    entry_points={
        "console_scripts": ["gendocs = docstring_generator.__main__:main"],
    },
)
