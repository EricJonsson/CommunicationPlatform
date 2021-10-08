import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="UUGame",
    version="1.0.0",
    author="Group D",
    description="UUGame for 1DL251",
    long_description=long_description,
    long_description_content_type="text/markdown",
    package_dir={"": "UUGame"},
    packages=setuptools.find_packages(where="UUGame"),
    python_requires=">=3.9.6",
)