#!/usr/bin/env python
from setuptools import setup

# Read version from the package
with open('notification_server.py', 'r') as f:
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
    description="MCP server for Claude Desktop sound notifications on macOS",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Charles Adedotun",
    author_email="charles.adedotun8@gmail.com",
    url="https://github.com/charles-adedotun/notifications-mcp-server",
    py_modules=["notification_server"],  # Single-file module
    entry_points={
        "console_scripts": [
            "claude-notifications=notification_server:main",
        ],
    },
    install_requires=[
        "fastmcp>=0.7.0",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: MacOS X",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS :: MacOS X",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
)
