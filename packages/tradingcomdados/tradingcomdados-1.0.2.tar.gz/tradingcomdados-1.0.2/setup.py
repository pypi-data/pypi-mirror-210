from setuptools import find_packages, setup


VERSION = open('VERSION').read()
LONG_DESCRIPTION = open('README.md').read()


with open("requirements.txt", "r") as fp:
    reqs = fp.read().split("\n")


setup(
    name="tradingcomdados",
    packages=find_packages(include=["tradingcomdados"]),
    version=VERSION,
    description="tradingcomdados",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    author="Lucas Roberto Correa",
    install_requires=reqs,
    setup_requires=["pytest_runner"],
    tests_require=["pytest== 6.2.4"],
    tests_suite="tests",
)