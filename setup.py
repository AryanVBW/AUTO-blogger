#!/usr/bin/env python3
"""
Setup script for AUTO-blogger
Copyright © 2025 AryanVBW
GitHub: https://github.com/AryanVBW
"""

from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Read requirements
with open('requirements.txt') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="auto-blogger",
    version="1.0.0",
    author="AryanVBW",
    author_email="AryanVBW@gmail.com",
    description="Automated WordPress Blog Posting Tool with AI Integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AryanVBW/AUTO-blogger",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: Content Management System",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "autoblog=gui_blogger:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.json", "*.md", "*.txt", "*.png", "*.ico"],
    },
    keywords="wordpress, blog, automation, ai, content, posting, seo",
    project_urls={
        "Bug Reports": "https://github.com/AryanVBW/AUTO-blogger/issues",
        "Source": "https://github.com/AryanVBW/AUTO-blogger",
        "Documentation": "https://github.com/AryanVBW/AUTO-blogger/blob/main/README.md",
    },
)