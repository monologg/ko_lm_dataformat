import os
import sys
from setuptools import setup, find_packages

if sys.version_info < (3, 6):
    sys.exit("Sorry, Python >= 3.6 is required for ko_lm_dataformat")

with open("requirements.txt") as f:
    require_packages = [line.strip() for line in f]

with open(os.path.join("ko_lm_dataformat", "version.txt")) as f:
    version = f.read().strip()

setup(
    name="ko_lm_dataformat",
    version=version,
    author="Jangwon Park",
    author_email="adieujw@gmail.com",
    description="A utility for storing and reading files for Korean LM training.",
    long_description=open("./README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/monologg/ko_lm_dataformat",
    packages=find_packages(exclude=["tests"]),
    python_requires=">=3.6",
    zip_safe=False,
    include_package_data=True,
    install_requires=require_packages,
)
