from setuptools import setup, find_packages
import codecs
import os
from ipsocgen.common.version import __IPSOCGEN_VERSION__

VERSION = __IPSOCGEN_VERSION__
DESCRIPTION = 'Generic SoC builder in HDL'
LONG_DESCRIPTION = 'Build SoCs (System-on-Chip) and MPSoCs (Multi-Processor) through yaml configuration files.'

here = os.path.abspath(os.path.dirname(__file__))
with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

# Setting up
setup(
    name="ipsocgen",
    version=VERSION,
    author="aignacio (Anderson Ignacio)",
    author_email="<anderson@aignacio.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    url='https://github.com/aignacio/ipsocgen',
    packages=find_packages(),
    package_data={
        '':['common/schemas/*.yaml', 'common/templates/*.txt']
    },
    include_package_data=True,
    install_requires=[
        'tabulate',
        'argparse',
        'pyyaml',
        'cerberus',
        'jinja2'
    ],
    keywords=['soc', 'mpsoc', 'hdl',  'verilog', 'systemverilog', 'builder'],
    entry_points = {
        'console_scripts': ['ipsocgen=ipsocgen.ipsocgen_cli:main'],
    },
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
