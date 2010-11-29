from setuptools import setup, find_packages

setup(
    name = "protocoller",
    version = "0.1",
    url = 'http://github.com/quoter/protocoller',
    license = 'MIT',
    description = "An aggregator of cross country race protocols.",
    author = 'Dmitry Sukhov',
    packages = find_packages('src'),
    package_dir = {'': 'src'},
    install_requires = ['setuptools'],
)
 
