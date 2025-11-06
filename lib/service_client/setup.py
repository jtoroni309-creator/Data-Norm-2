"""Setup script for service_client library"""

from setuptools import setup, find_packages

setup(
    name="service-client",
    version="1.0.0",
    description="Service-to-service communication library for Aura Audit AI",
    packages=find_packages(),
    install_requires=[
        "httpx>=0.27.0",
        "tenacity>=8.2.0",
    ],
    python_requires=">=3.11",
)
