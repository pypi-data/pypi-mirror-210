from setuptools import setup

setup(
    name='Candataloader',
    version='1.0.0',
    author='PhongPhat',
    author_email='19522010@gm.uit.edu.vn',
    description='A library for downloading datasets',
    packages=['download_dataset'],
    install_requires=[
        'requests',  
        'numpy>=1.0', 
    ],
)