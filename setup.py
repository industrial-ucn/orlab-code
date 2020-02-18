import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="industrialucn", # Replace with your own username
    version="0.1.6",
    author="Hernan Caceres",
    author_email="idustrial@ucn.cl",
    description="Generic tool for numerical experiments",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://industrial.ucn.cl",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: Free for non-commercial use",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.7",
        "Topic :: Scientific/Engineering"
    ],
    python_requires='>=3.7',
)
