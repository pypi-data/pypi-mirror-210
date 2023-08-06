from setuptools import setup, find_packages, find_namespace_packages

setup(
    name = "ugot",
    version = "0.1.2",
    description = "ugot-Python SDK",
    long_description = "",

    packages = find_packages(include=["ugot","ugot.*"]),
    # package_data = {"ugot": ["*"],
    #                 },
    # packages=find_packages(),
    # include_package_data = True,
    platforms = "any",
    install_requires = [
        'concurrent-log-handler',
        'grpcio',
        'protobuf',
        'grpcio-tools',
        'wheel',
        'zeroconf',
    ]
)