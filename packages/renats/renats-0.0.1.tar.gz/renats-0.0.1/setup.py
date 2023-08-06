from setuptools import setup, find_packages

with open("README.md", "r") as readme_file:
    readme = readme_file.read()

requirements = ["msgpack>=1.0.5", "nats-py>=2.2.0"]

setup(
    name="renats",
    version="0.0.1",
    author="Respirens",
    author_email="thesergiyprotsanin@gmail.com",
    description="NATS requests for humans",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/Respirens/renats/",
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
)
