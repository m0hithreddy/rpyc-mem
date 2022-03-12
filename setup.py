from setuptools import setup

setup(
    version=open("rpyc_mem/_version.py").readlines()[-1].split()[-1].strip("\"'")
)
