"""Setup script for event_bus library"""

from setuptools import setup, find_packages

setup(
    name="event-bus",
    version="1.0.0",
    description="Redis-based event bus for Aura Audit AI microservices",
    packages=find_packages(),
    install_requires=[
        "redis>=5.0.0",
        "pydantic>=2.5.0",
    ],
    python_requires=">=3.11",
)
