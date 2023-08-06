import os
from setuptools import setup, find_packages

package_data = {}

for package in find_packages():
    package_data[package] = ["*.pyi"]

version = os.environ.get('PYPIVERSION')
setup_args = dict(
    name="oak9_tython",
    version=version,
    packages=find_packages(),
    package_data=package_data,
    author="Claudio Balbin, Brandon Nicoll",
    author_email="bnicoll@oak9.io",
    description="",
    readme="README.md",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    project_urls={
        "Homepage": "https://github.com/oak9io/tython",
        "Bug Tracker": "https://github.com/oak9io/tython/issues",
    },
    install_requires=[
        'gitpython==3.1.31',
        'protobuf>=4.23.1',
        'requests>=2.31.0',
        'structlog>=23.1.0',
    ],
    python_requires=">=3.11",
    long_description="oak9 Tython Python framework",
    long_description_content_type="text/markdown",
    # Add these lines to enable debugging:
    options={
        'build_ext': {
            'debug': True
        }
    }
)

if __name__ == '__main__':
    setup(**setup_args)
