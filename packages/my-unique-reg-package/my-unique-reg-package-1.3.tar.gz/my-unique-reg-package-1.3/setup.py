import setuptools

with open("README.txt", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='my-unique-reg-package',
    version='1.3',
    description='Different Types of Regression',
    author='Sahraoui Tarek Ziad',
    author_email='tziad2027@gmail.com',
    packages=setuptools.find_packages(),
    py_modules=['reg.regi'],
)
