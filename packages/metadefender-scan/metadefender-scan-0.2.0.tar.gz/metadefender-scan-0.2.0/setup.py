from os import path

from setuptools import setup


def get_readme_content():
    """Get content of README.md file

    Returns:
        str: README.md content
    """
    readme_dir = path.abspath(path.dirname(__file__))
    with open(path.join(readme_dir, "README.md"), encoding="utf-8") as fd:
        long_desc = fd.read()

    return long_desc


setup(
    name="metadefender-scan",
    description="Command line tool which allows to send files to MetaDefender server and fetch scanning results.",
    long_description=get_readme_content(),
    long_description_content_type="text/markdown",
    author="mkot02",
    url="https://github.com/mkot02/metadefender_scan",
    version="0.2.0",
    packages=["metadefender"],
    package_dir={"": "src"},
    package_data={"metadefender": ["py.typed"]},
    python_requires=">=3.6",
    install_requires=[
        "PyYAML",
        "requests",
    ],
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: System :: Software Distribution",
    ],
    entry_points={
        "console_scripts": "metadefender-scan=metadefender:main",
    },
)
