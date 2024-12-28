from setuptools import setup, find_packages

setup(
    name='ecocore',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'sdl2',
    ],
    description='A custom game library',
    author='Noah Payne',
    author_email='noahalexanderpayne@gmail.com',
    url='https://github.com/noahpyne1/EcoCore',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
