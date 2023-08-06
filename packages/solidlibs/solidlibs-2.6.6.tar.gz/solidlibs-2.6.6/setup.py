'''
    Set up for open source libraries.

    Copyright 2018-2023 solidlibs
    Last modified: 2023-05-24
'''

import os.path
import setuptools

# read long description
with open(os.path.join(os.path.dirname(__file__), 'README.md'), 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name="solidlibs",
    version="2.6.6",
    author="solidlibs",
    maintainer="solidlibs",
    description="Open source python and django enhancements",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="locks logs log-parser openssl",
    license="GNU General Public License v3 (GPLv3)",
    url="https://github.com/safeapps/solidlibs/",
    download_url="https://github.com/safeapps/solidlibs/",
    project_urls={
        "Source Code": "https://github.com/safeapps/solidlibs/",
    },
    include_package_data=True,
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX :: Linux",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
         ],
    entry_points={
    },
    setup_requires=['setuptools-markdown'],
    install_requires=[],
    python_requires=">=3.9",
)
