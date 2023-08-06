# coding: utf-8
import setuptools

# VERSION NUMBER OBTAINED FROM setup.cfg FILE

description = "hdb++ python3 API"

if __name__ == "__main__":
    setuptools.setup(
    name="pyhdbpp",
#    version=version,
    license='LGPL-3+',
    packages=setuptools.find_packages(),
    description=description,
    long_description="Extract data from HDB++ Tango Archiving Systems, using either "
    "MariaDB or TimeScaleDB",
    author="Sergi Rubio, Damien Lacoste",
    author_email="info@tango-controls.org",
    )
