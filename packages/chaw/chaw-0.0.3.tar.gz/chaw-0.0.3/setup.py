from setuptools import setup, find_packages

VERSION = '0.0.3' 
DESCRIPTION = 'Wrapper for the Companies House API'
LONG_DESCRIPTION = 'Wrapper for the Companies House API'

setup(
        name="chaw", 
        version=VERSION,
        author="Morgan Thomas",
        author_email="morgan@morganthomas.uk",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(where="src"),
        package_dir={"": "src"},
        install_requires=['requests>=2.31.0'],   
        keywords=['python', 'companies house', 'uk', 'government', 'businesses'],
)