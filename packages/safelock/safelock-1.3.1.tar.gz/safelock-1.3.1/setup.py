'''
    Set up for safelock

    Copyright 2018-2023 safeapps
    Last modified: 2023-05-24
'''

import os.path
import setuptools

# read long description
with open(os.path.join(os.path.dirname(__file__), 'README.md'), 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name="safelock",
    version="1.3.1",
    author="safeapps",
    maintainer="safeapps",
    description="Safelock gives you simple systemwide multithread, multiprocess, multiprogram locks.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="locks multiprocess multithread multiinstance",
    license="GNU General Public License v3 (GPLv3)",
    url="https://github.com/safeapps/safelock/",
    download_url="https://github.com/safeapps/safelock/",
    project_urls={
        "Source Code": "https://github.com/safeapps/safelock/",
    },
    include_package_data=True,
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX :: Linux",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
         ],
    py_modules=["safelock"],
    scripts=['sbin/safelock'],
    entry_points={
    },
    data_files=[],
    setup_requires=['setuptools-markdown'],
    install_requires=['solidlibs', 'safelog'],
    python_requires=">=3.5",
)
