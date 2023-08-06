from setuptools import setup, find_packages


def requirements():
    with open("requirements.txt", "r") as f:
        return f.read().splitlines()


with open("README.md", "r") as fh:
    long_description = fh.read()
setup(
    name="hashkern",
    version="0.3.0",
    author="Mouhsen Ibrahim",
    author_email="mouhsen.ibrahim@gmail.com",
    description="A tool for managing resources in a mono repository",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Topic :: Software Development",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src", "tests": "tests"},
    python_requires=">=3.7",
    entry_points={"console_scripts": ["haks=hash.cli:main"]},
    packages=find_packages("src"),
    install_requires=requirements(),
    project_urls={
        "Documentation": "https://hashkern.readthedocs.io/en/latest/index.html",
        "Source": "https://gitlab.com/hash-platform/hashkern",
    },
)
