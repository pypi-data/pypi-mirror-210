from setuptools import setup, find_packages
from gpao_utils import _version

VERSION = _version.__version__
DESCRIPTION = "Utils for gpao project"
LONG_DESCRIPTION = "Library used for build project with ign-gpao"

# Setting up
setup(
    # the name must match the folder name 'verysimplemodule'
    name="ign-gpao-utils",
    version=VERSION,
    author="Yoann Apel",
    author_email="<yoann.apel@ign.fr>",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    keywords=['python', 'gpao', 'utils'],

)
