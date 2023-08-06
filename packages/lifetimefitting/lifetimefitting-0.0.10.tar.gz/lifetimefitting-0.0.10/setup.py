from setuptools import find_packages, setup

with open("README.md", "r", encoding = "utf-8") as fh:
    long_description = fh.read()

setup(
    name = "lifetimefitting",
    version = "0.0.10",
    author = "Adrea Snow",
    author_email = "adrea.snow@gmail.com",
    description = "PicoHarp TCSPC lifetime fitting tool",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = "https://github.com/adreasnow/LifetimeFittingTool",
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir = {"": "app"},
    packages = find_packages(where="app"),
    extras_require = {"dev": ["twine>=4.0.2"]},
    install_requires=['matplotlib', 'numpy', 'scipy', 'pyqt5'],
    python_requires = ">=3.8",
)