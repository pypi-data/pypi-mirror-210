from setuptools import setup

setup(
    name='Candataloader',
    version='1.0.1',
    author='PhongPhat',
    author_email='19522010@gm.uit.edu.vn',
    description='A library for downloading datasets',
    packages=['Candataloader'],
    python_requires='>=3.6',
    install_requires=[
        'requests',  
        'numpy>=1.0', 
    ],
)