import setuptools

setuptools.setup(
    name="pyiir",
    version="0.0.6",
    author="jalex1",
    description="Wrapper around IIR",
    url="https://github.com/aeorxc/pyiir",
    project_urls={
        "Source": "https://github.com/aeorxc/pyiir",
    },
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=["requests", "cachetools", "pandas"],
    python_requires=">=3.8",
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
)
