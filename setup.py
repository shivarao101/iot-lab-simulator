"""Setup configuration for iot-lab-simulator package"""

from setuptools import setup, find_packages
import os

# Read the contents of README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = f.read().splitlines()

setup(
    name="iot-lab-simulator",
    version="1.0.0",
    author="Shivaprasad",
    author_email="shivarao101@gmail.com",
    description="A complete IoT Lab Simulator for educational purposes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/shivarao101/iot-lab-simulator",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Topic :: Education",
        "Topic :: Scientific/Engineering",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(exclude=["tests", "docs", "examples"]),
    python_requires=">=3.7",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=21.0",
            "flake8>=3.9",
            "twine>=3.4",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=0.5",
        ],
    },
    entry_points={
        "console_scripts": [
            "iot-lab-simulator=iot_lab_simulator.simulator:main",
        ],
        "gui_scripts": [
            "iot-lab-simulator-gui=iot_lab_simulator.simulator:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)