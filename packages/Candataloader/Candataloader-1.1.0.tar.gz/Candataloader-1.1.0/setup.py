from setuptools import setup

setup(
    name='Candataloader',
    version='1.1.0',
    author='PhongPhat',
    author_email='19522010@gm.uit.edu.vn',
    description='A library for downloading datasets',
    packages=['Candataloader'],
    install_requires=[
        'requests',
    ],
    python_requires='>=3.6',
)