"""Setup script for italian-tax-validators."""

from setuptools import setup, find_packages

setup(
    name="italian-tax-validators",
    version="1.0.0",
    packages=find_packages(exclude=["tests", "tests.*"]),
    python_requires=">=3.9",
    author="Michele Broggi",
    author_email="michele@broggi.work",
    description="Python library for validating Italian Codice Fiscale and Partita IVA",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/thesmokinator/italian-tax-validators",
    project_urls={
        "Bug Tracker": "https://github.com/thesmokinator/italian-tax-validators/issues",
        "Documentation": "https://github.com/thesmokinator/italian-tax-validators#readme",
        "Source Code": "https://github.com/thesmokinator/italian-tax-validators",
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Natural Language :: Italian",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Office/Business :: Financial",
    ],
    keywords="italian codice-fiscale partita-iva tax-id validation fiscal-code vat",
)
