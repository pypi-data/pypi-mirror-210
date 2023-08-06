import os
import re
import subprocess
import sys
import zipfile

from cloudshell.layer_one.core.helper.runtime_configuration import RuntimeConfiguration

CONFIG_FILE = "package_config.yml"
PACKAGE_FILES_KEY = "PACKAGE_FILES"
COLLECT_DEPENDENCIES_KEY = "COLLECT_DEPENDENCIES"
DEFAULT_FILES = [
    "datamodel",
    "main.py",
    "install_driver.bat",
    "driver_exe_template",
    "requirements.txt",
    "version.txt",
    "INSTALL.txt",
]
DEFAULT_PACKAGES = ("pip", "wheel", "setuptools")


def zip_driver(driver_path, driver_zip_file, files):
    with zipfile.ZipFile(driver_zip_file, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for name in files:
            _append_files(os.path.join(driver_path, name), zip_file)


def _append_files(path, zip_file):
    if os.path.isfile(path):
        rel_path = os.path.relpath(
            path, os.path.join(path, os.path.pardir, os.path.pardir)
        )
        zip_file.write(path, rel_path)
    else:
        for root, dirs, files in os.walk(path):
            for file_or_dir in files + dirs:
                if not file_or_dir.endswith(".pyc"):
                    full_path = os.path.join(root, file_or_dir)
                    rel_path = os.path.relpath(
                        full_path, os.path.join(path, os.path.pardir, os.path.pardir)
                    )
                    zip_file.write(full_path, rel_path)


def download_packages(packages_path, requirements):
    python_exec = sys.executable
    subprocess.call(
        [
            python_exec,
            "-m",
            "pip",
            "download",
            "-r",
            requirements,
            "-d",
            packages_path,
            "-q",
        ]
    )
    for lib_name in DEFAULT_PACKAGES:
        subprocess.call(
            [python_exec, "-m", "pip", "download", lib_name, "-d", packages_path, "-q"]
        )


def _print_help():
    message = """Usage: build_driver [OPTIONS]

Options:
    -h, --help  Show this message and exit.
    -i, --ignore-packages  Do not collect driver dependencies
    """
    print(message)  # noqa: T201


def build(args=None):
    if not args:
        args = sys.argv

    if "--help" in args[1:] or "-h" in args[1:]:
        _print_help()
        sys.exit(0)

    driver_path = os.getcwd()

    with open(os.path.join(driver_path, "version.txt")) as ver_file:
        version = ver_file.read().strip()

    config = RuntimeConfiguration(os.path.join(driver_path, CONFIG_FILE))

    file_list = config.read_key(PACKAGE_FILES_KEY, [])
    file_list.extend(DEFAULT_FILES)

    driver_folder_name = os.path.basename(driver_path)
    driver_name = re.sub("cloudshell-L1-", "", driver_folder_name, flags=re.IGNORECASE)
    driver_name = re.sub("-", "_", driver_name)
    if os.path.exists(os.path.join(driver_path, driver_name)):
        file_list.append(driver_name)
    else:
        print(f"Cannot find driver src folder {driver_name}")  # noqa: T201
        sys.exit(1)

    runtime_config = f"{driver_name}_runtime_config.yml"
    if os.path.exists(os.path.join(driver_path, runtime_config)):
        file_list.append(runtime_config)
    else:
        print("Cannot find driver runtime config {runtime_config}")  # noqa: T201
        sys.exit(1)

    driver_folder_name_ver = f"{driver_folder_name}-{version}"
    dist_path = os.path.join(driver_path, "dist")
    driver_zip_path = os.path.join(dist_path, driver_folder_name_ver + ".zip")

    if not os.path.exists(dist_path):
        os.mkdir(dist_path)

    if (
        "--ignore-packages" not in args[1:]
        and "-i" not in args[1:]
        and config.read_key(COLLECT_DEPENDENCIES_KEY, True)
    ):
        packages_path = os.path.join(driver_path, "packages")
        requirements_path = os.path.join(driver_path, "requirements.txt")

        if not os.path.exists(packages_path):
            os.mkdir(packages_path)

        download_packages(packages_path, requirements_path)
        file_list.append("packages")

    zip_driver(driver_path, driver_zip_path, set(file_list))


if __name__ == "__main__":
    build()
