"""
Setup file for common_core shared library
"""

from setuptools import setup, find_packages

setup(
    name="aura-common-core",
    version="1.0.0",
    description="Common core library for Aura Audit AI microservices",
    author="Aura Audit AI",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=[
        "fastapi>=0.109.0",
        "pydantic>=2.5.3",
        "python-jose[cryptography]>=3.3.0",
        "python-json-logger>=2.0.7",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.11",
    ],
)
