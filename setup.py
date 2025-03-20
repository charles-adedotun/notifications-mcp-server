#!/usr/bin/env python
from setuptools import setup, find_packages

# Read version from the package
with open('notifications/__init__.py', 'r') as f:
    for line in f:
        if line.startswith('__version__'):
            version = line.split('=')[1].strip().strip('"\'')
            break

# Read long description from README.md
with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name="notifications-mcp-server",
    version=version,
    description="MCP server for Claude Desktop sound and visual notifications on macOS",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Charles Adedotun",
    author_email="charles.adedotun8@gmail.com",
    url="https://github.com/charles-adedotun/notifications-mcp-server",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "claude-notifications=notifications.server:main",
        ],
    },
    install_requires=[
        "fastmcp>=0.4.1",
        "uv>=0.1.0",
    ],
    extras_require={
        'visual': [
            'pyobjc-core>=9.0',
            'pyobjc-framework-Cocoa>=9.0',
        ],
        'pync': [
            'pync>=2.0.3',
        ],
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
            'ruff>=0.0.260',
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: MacOS X",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS :: MacOS X",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Utilities",
    ],
    python_requires=">=3.10",
)