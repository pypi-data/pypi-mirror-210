import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='gadapt',
    version='0.2.12',
    author="Zoran Jankovic",
    author_email='bpzoran@yahoo.com',
    url='https://github.com/bpzoran/gadapt',
    packages=setuptools.find_packages(),
    long_description=long_description,
    description="GAdapt: A Python Library for Self-Adaptive Genetic Algorithm."
)