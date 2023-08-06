
from setuptools import setup, find_packages

setup(
    name="climeon",
    packages=find_packages(),
    version="1.3.0",
    license="MIT",
    description="Climeon API client",
    long_description="Climeon API client",
    author="Emil Hjelm",
    author_email="emil.hjelm@climeon.com",
    keywords=["climeon", "REST", "API"],
    python_requires=">=3.7.1",
    install_requires=[
        "plotly>=5,<6",
        "plotly-resampler",
        "msal>=1.15.0,<2",
        "pandas>=1,<2",
        "requests",
        "dateparser>=1,<2"
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Operating System :: OS Independent"
    ]
)
