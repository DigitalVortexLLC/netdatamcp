"""Setup configuration for NetData MCP."""
from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="netdatamcp",
    version="1.0.0",
    description="HTTP-based MCP server for YANG and SNMP MIB data management",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Digital Vortex LLC",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "fastmcp>=0.2.0",
        "uvicorn>=0.27.0",
        "pyyaml>=6.0.1",
    ],
    entry_points={
        "console_scripts": [
            "netdatamcp=main:main",
            "netdatamcp-processor=netdatamcp.processor:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
