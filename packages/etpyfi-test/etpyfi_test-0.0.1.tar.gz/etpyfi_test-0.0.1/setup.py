from setuptools import setup, find_packages


with open("README.md", encoding="utf-8") as file:
    long_description = file.read()


VERSION = "0.0.1"
DESCRIPTION = "Eine Demonstration..."


setup(
    name="etpyfi_test",
    version=VERSION,
    author="Thomas Benkenstein",
    author_email="thomas.benkenstein@experteach.de",
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["numpy>=1.0.0", "pandas"],
    keywords=["python", "code"],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.10",
    ],
)