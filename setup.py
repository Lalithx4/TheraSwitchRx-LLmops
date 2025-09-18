from setuptools import setup, find_packages
with open("requirements.txt") as f:
    requirements = f.read().splitlines()


setup(
    name="TheraSwitchRx",
    version="0.1",
    author="Lalith - MedQ AI",
    description="Professional Medical Alternatives Recommender - AI-Powered Medicine Alternative Discovery",
    packages=find_packages(),
    install_requires=requirements,

)    