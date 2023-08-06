import os

from setuptools import find_packages, setup

with open(os.path.join("version.txt")) as version_file:
    version_from_file = version_file.read().strip()

with open("requirements.txt") as f_required:
    required = f_required.read().splitlines()

with open("test_requirements.txt") as f_tests:
    required_for_tests = f_tests.read().splitlines()


setup(
    name="cloudshell-l1-networking-core",
    author="Quali",
    author_email="info@quali.com",
    packages=find_packages(),
    install_requires=required,
    python_requires="~=3.7",
    tests_require=required_for_tests,
    version=version_from_file,
    description="QualiSystems CloudShell L1 networking core package",
    long_description="QualiSystems CloudShell L1 networking core package",
    long_description_content_type="text/x-rst",
    url="https://github.com/QualiSystems/cloudshell-l1-networking-core",
    package_data={"core": ["data/*.yml", "data/*.json", "*.txt"]},
    entry_points={
        "console_scripts": [
            "build_driver = cloudshell.layer_one.tools.build_driver:build"
        ]
    },
    include_package_data=True,
    license="Apache Software License 2.0",
    zip_safe=False,
    keywords="core cloudshell quali layer-one",
    test_suite="tests",
)
