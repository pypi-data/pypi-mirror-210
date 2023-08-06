"""Python setup.py for klops package"""
import io
import os
from setuptools import find_packages, setup


def read(*paths, **kwargs):
    """Read the contents of a text file safely.
    >>> read("klops", "VERSION")
    '0.0.3'
    >>> read("README.md")
    ...
    """

    content = ""
    with io.open(
        os.path.join(os.path.dirname(__file__), *paths),
        encoding=kwargs.get("encoding", "utf8"),
    ) as open_file:
        content = open_file.read().strip()
    return content


requirements = [
    "click",
    "dvc",
    "google-cloud",
    "google-cloud-container",
    "google-cloud-storage",
    "google-auth",
    "hyperopt",
    "kubernetes",
    "joblib",
    "matplotlib",
    "mlflow",
    "scikit-learn",
    "seldon-core",
    "pandas",
    "numpy",
    "tqdm"
]
requirements_test = [
    "pytest",
    "coverage",
    "flake8",
    "black",
    "isort",
    "pytest-cov",
    "codecov",
    "mypy",
    "gitchangelog",
    "mkdocs"
]


setup(
    name="klops",
    version=read("klops", "VERSION"),
    description="Klops: Koin Machine Learning Ops",
    url="https://gitlab-engineering.koinworks.com/data-team/klops/",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    author="Koinworks Data Team",
    packages=find_packages(exclude=["tests", ".github"]),
    install_requires=requirements,
    entry_points={
        "console_scripts": ["klops = klops.__main__:main"]
    },
    extras_require={"test": requirements_test},
    package_data={'': ['klops/*.json']},
    include_package_data=True
)
