import setuptools

from os import path


with open("README.md", "r") as fh:
    long_description = fh.read()


here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'requirements.txt')) as f:
    requirements = []
    for line in f:
        requirements.append(line)


setuptools.setup(
    name="phone_bills",
    version="0.0.1",
    author="Allan Silva",
    author_email="allan.tavares@allantavares.com.br",
    description="Phone Bills API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/allan-silva/test-phone-bills",
    packages=setuptools.find_packages(),
    install_requires=requirements,
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        ],
)
