from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))


VERSION = '0.0.3'
DESCRIPTION = 'Coming soon'
LONG_DESCRIPTION = 'todo'

# Setting up
setup(
    name="psychopy-usbToBNC",
    version=VERSION,
    author="Labeo Technologies(Christophe Cloutier-Tremblay)",
    author_email="<Christophe@labeotech.com>",
    entry_points={'psychopy.visual': 'MyStim = psychopy_plugin:MyStim'},
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=['Psychopy'],
    keywords=['python'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)