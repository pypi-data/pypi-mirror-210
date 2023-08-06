from setuptools import setup, find_packages

setup(
    name='Candataloader',
    version='1.0.9',
    author='PhongPhat',
    author_email='19522010@gm.uit.edu.vn',
    description='A library for downloading datasets',
    packages=find_packages(),
    package_data={
        '': ['datasets/*.csv'],  # Include all CSV files in the datasets folder
    },
    python_requires='>=3.6',
    install_requires=[
    ],
)