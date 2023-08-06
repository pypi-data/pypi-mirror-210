from setuptools import setup, find_packages

setup(
    name='remla23_team17_lib',
    version='v1.0.6',
    author='remla23-team17',
    author_email='remyduijsens@gmail.com',
    description='Library for retrieving repo versions',
    long_description_content_type="text/markdown",
    long_description='Library for retrieving repo versions',
    url='https://github.com/remla23-team17/lib',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.9',
    ],
    packages=find_packages()
)
