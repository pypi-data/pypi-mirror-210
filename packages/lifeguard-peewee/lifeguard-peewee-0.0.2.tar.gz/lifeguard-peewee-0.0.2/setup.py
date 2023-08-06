from setuptools import find_packages, setup
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="lifeguard-peewee",
    version="0.0.2",
    url="https://github.com/LifeguardSystem/lifeguard-peewee",
    author="Diego Rubin",
    author_email="contact@diegorubin.dev",
    license="GPL2",
    scripts=[],
    include_package_data=True,
    description="Lifeguard integration with SQL servers using peewee",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=["lifeguard", "peewee"],
    classifiers=["Development Status :: 3 - Alpha"],
    packages=find_packages(),
)
