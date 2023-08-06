from setuptools import setup, find_packages

setup(
    name='Candataloader',
    version='1.0.4',
    author='PhongPhat',
    author_email='19522010@gm.uit.edu.vn',
    description='A library for downloading datasets',
    packages=find_packages(),
    package_data={
        'Candataloader': ['datasets/Survival Analysis Dataset for automobile IDS.csv', 'datasets/SynCAN.csv'],
    },
    python_requires='>=3.6',
    install_requires=[
        'requests',  
        'numpy>=1.0', 
    ],
)