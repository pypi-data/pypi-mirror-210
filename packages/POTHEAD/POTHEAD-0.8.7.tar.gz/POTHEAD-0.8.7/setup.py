import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

test_deps = ["aiohttp", "werkzeug", "tblib", "timeout-decorator"]

setuptools.setup(
    name="POTHEAD",
    version="0.8.7",
    author="Ulrik Mikaelsson",
    author_email="ulrik.mikaelsson@gmail.com",
    description="A reverse-http proxy implementation for non-concurrent requests",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/rawler/pothead",
    packages=setuptools.find_packages(),
    install_requires=["psutil", "werkzeug>=2.1", "tblib"],
    tests_require=test_deps,
    extras_require={
        "test": test_deps,
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
)
