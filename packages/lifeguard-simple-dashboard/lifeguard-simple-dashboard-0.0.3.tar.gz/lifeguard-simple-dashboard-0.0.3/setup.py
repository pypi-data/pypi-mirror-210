from setuptools import find_packages, setup

setup(
    name="lifeguard-simple-dashboard",
    version="0.0.3",
    url="https://github.com/LifeguardSystem/lifeguard-simple-dashboard",
    author="Diego Rubin",
    author_email="contact@diegorubin.dev",
    license="GPL2",
    scripts=[],
    include_package_data=True,
    description="Implementation of a simple Lifeguard Dashboard",
    install_requires=["lifeguard"],
    classifiers=["Development Status :: 3 - Alpha"],
    packages=find_packages(),
)
