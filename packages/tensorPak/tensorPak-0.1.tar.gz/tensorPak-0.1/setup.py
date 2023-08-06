from setuptools import setup, find_packages

setup(
    name='tensorPak',
    version='0.1',
    description='Custom SKLearn package by N.K.Bhansodhe',
    author='Parmish_Verma',
    author_email='pcq02960@zslsz.com',
    packages=find_packages(include=['tensorPak', 'tensorPak.*']),
    package_data={
        'tensorPak': ['1.txt', '2.txt', '3.txt', '4.txt', '5.txt', '11.txt', '12.txt', '13.txt', '14.txt', '15.txt', '16.txt', '17.txt', '18.txt', '19.txt', '20.txt'],
    },
)
