from setuptools import setup, find_packages

setup(
    name='m4ai',
    version='1.0.3',
    author='zachary',
    author_email='zacharylyj@example.com',
    description='冰淇淋',
    long_description='现在我有冰淇淋',
    long_description_content_type='text/markdown',
    url='https://github.com/zacharylyj/m4ai',
    packages=find_packages(),
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    install_requires=[
        'numpy>=1.20.0',
        # Add any other dependencies here
    ],
)