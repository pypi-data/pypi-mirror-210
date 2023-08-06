import setuptools

setuptools.setup(
    name="pyplattsapi",
    version="0.0.12",
    author="aeorxc",
    description="Wrapper around Platts API",
    url="https://github.com/aeorxc/pyplattsapi",
    project_urls={
        "Source": "https://github.com/aeorxc/pyplattsapi",
    },
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=["pandas", "requests", "cachetools"],
    python_requires=">=3.8",
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
)
