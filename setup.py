from setuptools import setup, find_packages

setup(
    name="ara-1-autonomous-research-agent",
    version="1.0.0",
    description="Autonomous Financial Research Agent with Multi-Source Synthesis (Project 1A)",
    packages=find_packages(exclude=["tests"]),
    python_requires=">=3.10",
    install_requires=[
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
        "pydantic>=2.0.0",
        "tenacity>=8.2.0",
        "rich>=13.0.0",
        "numpy>=1.24.0",
    ],
    extras_require={"dev": ["pytest>=8.0.0"]},
)
