import os
import pathlib

import setuptools

# Read the contents of your README file
# with open("README.md", "r", encoding="utf-8") as fh:
#     long_description = fh.read()

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

readme_path = pathlib.Path("README.md")
requirements_path = pathlib.Path("requirements.txt")

setuptools.setup(
    name="aeroapi-python",
    version="1.1.2",
    description='FlightAware AeroAPI Caller for Python',
    long_description=readme_path.read_text(),
    long_description_content_type="text/markdown",
    url="https://github.com/derens99/aeroapi-python",
    author="Deren S",
    author_email="derens9999@gmail.com",
    license="MIT",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Education :: Testing",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
    keywords="python aeroapi flightaware flightaware-api flightaware-aeroapi flightaware-aeroapi-python flightaware-aeroapi-python3 flightaware-aeroapi-python3.5 flightaware-aeroapi-python3.6 flightaware-aeroapi-python3.7 flightaware-aeroapi-python3.8 flightaware-aeroapi-python3.9",
    py_modules=[
        "aeroapi_python.APICaller",
        "aeroapi_python.AeroAPI",
        "aeroapi_python.Airports",
        "aeroapi_python.Flights",
        "aeroapi_python.History",
        "aeroapi_python.Miscellaneous",
        "aeroapi_python.Operators",
    ],
    install_requires=requirements_path.read_text().splitlines(),
    python_requires=">=3.5",
)
