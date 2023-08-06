from setuptools import setup, find_packages

REQUIRED_PACKAGES = [
    'viggocore>=1.0.0,<2.0.0',
    'viggolocal>=1.0.0',
    'flask-cors'
]

setup(
    name="viggoparceiro",
    version="1.0.5",
    summary='ViggoParceiro Module Framework',
    description="ViggoParceiro Backend Flask REST service",
    packages=find_packages(exclude=["tests"]),
    install_requires=REQUIRED_PACKAGES
)
