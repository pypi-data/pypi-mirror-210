from setuptools import find_packages
import setuptools
import os

with open("README_PIP.md", "r") as fh:
    long_description = fh.read()
with open("requirements.txt","r") as req:
    required_packages = req.read().splitlines()

__version__ = '0.2.0'
__author__='Vishal, Koushik, Sudharshan, Vikneshwar, Bhanuja, Ajay'
__author_email__ = 'check-new@googlegroups.com'

setuptools.setup(
    name="cloud2",                
    version=__version__,                        
    author=__author__,  
    author_email=__author_email__,
    license= 'MIT',              
    description="AWS Cloud Audit Tool",
    long_description=long_description,     
    long_description_content_type="text/markdown",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    package_data={
        'common': ['templates/*.html'],
    },
    py_modules=['main'],
    entry_points={
        'console_scripts': [
            'cloud-audit-tool=main:Main.generate_aws_audit_report'
        ]
    },
    include_package_data=True,
    python_requires='>=3.6',                
    install_requires=required_packages,
)