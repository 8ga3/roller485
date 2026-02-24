from setuptools import find_packages, setup

setup(
    name="roller485",
    version="0.1.0",
    packages=find_packages(),
    install_requires=["kaitaistruct>=0.11", "pyserial>=3.5"],
    author="8ga3",
    description="A Python project for Unit Roller485",
    python_requires=">=3.9",
)
