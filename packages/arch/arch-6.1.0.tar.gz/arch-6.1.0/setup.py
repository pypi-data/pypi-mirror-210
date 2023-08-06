from setuptools import Command, Extension, find_packages, setup
from setuptools.command.build_ext import build_ext as _build_ext
from setuptools.dist import Distribution
from setuptools.errors import CCompilerError, ExecError, PlatformError

from collections import defaultdict
import fnmatch
import os
import pathlib

import pkg_resources

CYTHON_COVERAGE = os.environ.get("ARCH_CYTHON_COVERAGE", "0") in ("true", "1", "True")
if CYTHON_COVERAGE:
    print(
        "Building with coverage for cython modules, ARCH_CYTHON_COVERAGE="
        + os.environ["ARCH_CYTHON_COVERAGE"]
    )

try:
    from Cython.Build import cythonize

    CYTHON_INSTALLED = True
except ImportError:
    CYTHON_INSTALLED = False
    if CYTHON_COVERAGE:
        raise ImportError(
            "cython is required for cython coverage. Unset " "ARCH_CYTHON_COVERAGE"
        )


FAILED_COMPILER_WARNING = """
******************************************************************************
*                               WARNING                                      *
******************************************************************************

Unable to build binary modules for arch.  While these are not required to run
any code in the package, it is strongly recommended to either compile the
extension modules or to use numba.

******************************************************************************
*                               WARNING                                      *
******************************************************************************
"""


# prevent setup.py from crashing by calling import numpy before numpy is installed
class build_ext(_build_ext):
    def build_extensions(self) -> None:
        numpy_incl = pkg_resources.resource_filename("numpy", "core/include")

        for ext in self.extensions:
            if hasattr(ext, "include_dirs") and numpy_incl not in ext.include_dirs:
                ext.include_dirs.append(numpy_incl)
        _build_ext.build_extensions(self)


with pathlib.Path("requirements.txt").open() as requirements_txt:
    install_requires = [
        str(requirement)
        for requirement in pkg_resources.parse_requirements(requirements_txt)
    ]


cmdclass = {"build_ext": build_ext}


class BinaryDistribution(Distribution):
    def is_pure(self) -> bool:
        return False


class CleanCommand(Command):
    def run(self) -> None:
        raise NotImplementedError("Use git clean -xfd instead")

    def initialize_options(self) -> None:
        pass

    def finalize_options(self) -> None:
        pass


cmdclass["clean"] = CleanCommand

with open("README.md") as readme:
    description = readme.read()

package_data = defaultdict(list)
filetypes = ["*.csv", "*.csv.gz"]
for root, _, filenames in os.walk(os.path.join(os.getcwd(), "arch")):  # noqa: E501
    matches = []
    for filetype in filetypes:
        for filename in fnmatch.filter(filenames, filetype):
            matches.append(filename)
    if matches:
        package_data[".".join(os.path.relpath(root).split(os.path.sep))] = filetypes
package_data["arch"].append("py.typed")


def run_setup(binary: bool = True) -> None:
    if not binary:
        extensions = []
        import logging

        logging.warning(
            """
##############################################################################

Building arch WITHOUT compiling the binary. You should ensure that numba is
installed.

##############################################################################
"""
        )
    else:
        directives = {
            "language_level": "3",
            "cpow": True,
            "linetrace": CYTHON_COVERAGE,
            "boundscheck": False,
            "wraparound": False,
            "cdivision": True,
            "binding": True,
        }
        macros = [("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")]
        if CYTHON_COVERAGE:
            macros.append(("CYTHON_TRACE", "1"))

        ext_modules = []
        ext_modules.append(
            Extension(
                "arch.univariate.recursions",
                ["./arch/univariate/recursions.pyx"],
                define_macros=macros,
            )
        )
        ext_modules.append(
            Extension(
                "arch.bootstrap._samplers",
                ["./arch/bootstrap/_samplers.pyx"],
                define_macros=macros,
            )
        )
        extensions = cythonize(
            ext_modules, force=CYTHON_COVERAGE, compiler_directives=directives
        )

    setup(
        name="arch",
        license="NCSA",
        description="ARCH for Python",
        long_description=description,
        long_description_content_type="text/markdown",
        author="Kevin Sheppard",
        author_email="kevin.sheppard@economics.ox.ac.uk",
        url="https://github.com/bashtage/arch",
        packages=find_packages(),
        ext_modules=extensions,
        package_dir={"arch": "./arch"},
        cmdclass=cmdclass,
        keywords=[
            "arch",
            "ARCH",
            "variance",
            "econometrics",
            "volatility",
            "finance",
            "GARCH",
            "bootstrap",
            "random walk",
            "unit root",
            "Dickey Fuller",
            "time series",
            "confidence intervals",
            "multiple comparisons",
            "Reality Check",
            "SPA",
            "StepM",
        ],
        zip_safe=False,
        include_package_data=False,
        package_data=package_data,
        distclass=BinaryDistribution,
        classifiers=[
            "Development Status :: 5 - Production/Stable",
            "Intended Audience :: End Users/Desktop",
            "Intended Audience :: Financial and Insurance Industry",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: 3.10",
            "Programming Language :: Python :: 3.11",
            "License :: OSI Approved",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
            "Operating System :: POSIX",
            "Programming Language :: Python",
            "Programming Language :: Cython",
            "Topic :: Scientific/Engineering",
        ],
        install_requires=install_requires,
        python_requires=">=3.9",
    )


try:
    build_binary = CYTHON_INSTALLED
    build_binary &= os.environ.get("ARCH_NO_BINARY", None) not in ("1", "True", "true")
    run_setup(binary=build_binary)
except (
    CCompilerError,
    ExecError,
    PlatformError,
    OSError,
    ValueError,
):
    run_setup(binary=False)
    import warnings

    warnings.warn(FAILED_COMPILER_WARNING, UserWarning)
