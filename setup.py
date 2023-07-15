# Available at setup time due to pyproject.toml
import pathlib

from pybind11.setup_helpers import Pybind11Extension, build_ext
from setuptools import find_packages, setup

__version__ = "0.0.30"

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

# The main interface is through Pybind11Extension.
# * You can add cxx_std=11/14/17, and then build_ext can be removed.
# * You can set include_pybind11=false to add the include directory yourself,
#   say from a submodule.
#
# Note:
#   Sort input source files if you glob sources to ensure bit-for-bit
#   reproducible builds (https://github.com/pybind/python_example/pull/53)


class CustomBuildExt(build_ext):
    def run(self):
        # Include additional header file directories
        self.include_dirs.append("src/docstringFormat.hpp")
        super().run()


ext_modules = [
    Pybind11Extension(
        "docstring_generator_ext",
        [
            "src/docstringFormat.cpp",
        ],
    ),
]

setup(
    name="docstring_generator_ext",
    version=__version__,
    url="https://github.com/FelixTheC/docstring_generator",
    license="MIT",
    author="FelixTheC",
    author_email="fberndt87@gmail.com",
    description="Generate Docstrings with type-hint information",
    long_description=README,
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: Utilities",
        "Topic :: Software Development :: Documentation",
        "Typing :: Typed",
    ],
    ext_modules=ext_modules,
    extras_require={"test": "pytest"},
    # Currently, build_ext only provides an optional "highest supported C++
    # level" feature, but in the future it may provide more features.
    cmdclass={"build_ext": CustomBuildExt},
    zip_safe=False,
    python_requires="<3.12",
)
