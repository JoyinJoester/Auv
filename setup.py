"""
Setup configuration for AUV (Automatic file organization Utilities)
"""

from setuptools import setup, find_packages
import os

# Read README for long description
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    requirements = []
    if os.path.exists("requirements.txt"):
        with open("requirements.txt", "r", encoding="utf-8") as f:
            requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    return requirements

setup(
    name="auv",
    version="1.0.0",
    author="JoyinJoester",
    author_email="",
    description="A powerful command-line file organization tool",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/JoyinJoester/Auv",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: System :: Filesystems",
        "Topic :: Utilities",
    ],
    python_requires=">=3.7",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "auv=auv.cli:main",
        ],
    },
    keywords="file organization automation cli tool",
    project_urls={
        "Bug Reports": "https://github.com/JoyinJoester/Auv/issues",
        "Source": "https://github.com/JoyinJoester/Auv",
        "Documentation": "https://github.com/JoyinJoester/Auv/blob/main/README.md",
    },
)