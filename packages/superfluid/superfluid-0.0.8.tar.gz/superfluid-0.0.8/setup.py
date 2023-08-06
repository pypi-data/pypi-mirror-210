from setuptools import find_packages, setup

with open("README.md") as f:
    long_description = f.read()

setup(
    name="superfluid",
    version="0.0.8",
    description="Python SDK for the Superfluid Protocol",
    package_dir={"": "main"},
    packages=find_packages(where="main"),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Godspower-Eze/superfluid.py",
    author="Godspower-Eze",
    author_email="Godspowereze260@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent"
    ],
    install_requires=["web3 == 6.3.0"],
    extras_require={
        "dev": ["twine>=4.0.2"]
    },
    python_requires=">=3"
)
