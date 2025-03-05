from setuptools import setup, find_packages

setup(
    name="gwtm",
    version="0.1.0",
    packages=["gwtm"],
    package_dir={"gwtm": "src"},
    entry_points={
        "console_scripts": [
            "gwtm=gwtm.main:main",
        ],
    },
    python_requires=">=3.7",
)