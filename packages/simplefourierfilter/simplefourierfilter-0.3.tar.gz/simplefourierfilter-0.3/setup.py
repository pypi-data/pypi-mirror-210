from setuptools import setup

setup(
    name='simplefourierfilter',
    version='0.3',
    description='Simple FFT based library for noise reduction',
    py_modules=['simplefourierfilter'],
    install_requires=[
        'numpy',
        'matplotlib'
    ],
)
