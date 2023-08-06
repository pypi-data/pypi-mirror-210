import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="plasIDome",
    version="1.0.0",
    author="Jo Hendrix",
    author_email="jrhendrix36@gmail.com",
    description="A tool to detect plasmids and contamination in bacterial and archaeal genome assemblies",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jrhendrix/plasIDome",
    scripts=['bin/plasIDome'],
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=['biopython'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)