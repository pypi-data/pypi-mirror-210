import setuptools

with open("README.txt", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='regi',
    version='2.1',
    description='Different Types of Regression',
    author='Sahraoui Tarek Ziad',
    author_email='tziad2027@gmail.com',
    packages=setuptools.find_packages(),
    py_modules=['regi.regi'],
)
