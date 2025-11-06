"""
ISS Module Setup Configuration
Integrated Starship Systems Module - A comprehensive logging and data management system
"""

from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

# Read requirements from requirements.txt
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="iss-module",
    version="1.0.0",
    author="ISS Module Development Team",
    author_email="dev@iss-module.com",
    description="Integrated Starship Systems Module - A comprehensive logging and data management system",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/iss-module",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Logging",
        "Topic :: Database :: Database Engines/Servers",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "pre-commit>=3.0.0",
        ],
        "docs": [
            "sphinx>=6.0.0",
            "sphinx-rtd-theme>=1.2.0",
            "myst-parser>=1.0.0",
        ],
        "analysis": [
            "visidata>=2.11",
            "pandas>=2.0.0",
            "matplotlib>=3.7.0",
            "seaborn>=0.12.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "iss=iss_module.cli:main",
            "iss-server=iss_module.api.main:run_server",
            "iss-log=iss_module.captain_mode:cli_main",
        ],
    },
    include_package_data=True,
    package_data={
        "iss_module": [
            "templates/*.html",
            "static/**/*",
            "data/**/*",
        ],
    },
    keywords=[
        "logging",
        "data-management",
        "captain-log",
        "journal",
        "api",
        "web-interface",
        "stardate",
        "export",
        "analytics"
    ],
    project_urls={
        "Bug Reports": "https://github.com/your-org/iss-module/issues",
        "Source": "https://github.com/your-org/iss-module",
        "Documentation": "https://iss-module.readthedocs.io/",
        "Changelog": "https://github.com/your-org/iss-module/blob/main/CHANGELOG.md",
    },
    zip_safe=False,
)