import pathlib

from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()


setup(
    name="docstring_generator",
    version="0.0.1",
    packages=[
        "src",
    ],
    url="https://github.com/FelixTheC/docstring_generator",
    license="MIT",
    author="felix",
    author_email="felixeisenmenger@gmx.net",
    description="Generate Docstrings with type-hint informations",
    long_description=README,
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
    python_requires=">=3.7",
    install_requires=["click", "strongtyping"],
)
