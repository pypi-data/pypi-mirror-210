from setuptools import setup

setup(
    name='simplefourierfilter',
    version='0.1',
    description='Simple FFT based library for noise reduction',
    py_modules=['simplefourierfilter'],
    install_requires=[
        'numpy',
        'matplotlib'
    ],
)
