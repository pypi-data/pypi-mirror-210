import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="probetools",
    version="0.1.11",
    author="Kevin Kuchinski",
    author_email="kevin.kuchinski@bccdc.ca",
    description="Hybridization probe design for targeted genomic sequencing of diverse and hypervariable viral taxa",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kevinkuchinski/probetools",
    project_urls={
        "Bug Tracker": "https://github.com/kevinkuchinski/probetools/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.7",
    entry_points={
    'console_scripts': [
        'probetools = probetools.probetools_v_0_1_11:main',
    ],
    }
)
