from setuptools import setup, find_packages

with open("README.md", "r", encoding = "utf-8") as fh:
    long_description = fh.read()

setup(
    author='Sunny Dung',
    name='apiquotamanager',
    version='0.0.1',
    description='API Quota Manager Python',
    author_email = "sdung@jobsync.com",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages = find_packages(),
    python_requires = ">=3.8"
)