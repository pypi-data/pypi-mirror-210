from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='SIOTCommon',
    version='0.1.5',
    packages=find_packages(),
    install_requires=requirements,
    author='Anton Persson',
    author_email='Antonnilspersson@gmail.com',
    description='Common operations for sweiot microservices',
    url='https://github.com/AntonNPersson/SweIoTServices.git',
    classifiers=[
        'Programming Language :: Python :: 3.10',
        'Operating System :: OS Independent',
    ],
)
