# +
from setuptools import find_packages, setup

setup(
    name = "keystem",
    version = "1.0.3",
    author = "Naga",
    author_email = "naga@caspai.in",
    description = "This project helps to have git version for S3 buckets."  ,
    url = "https://github.com/Nagakiran1/keystem.git",
    py_modules=['keystem.keyroots', 'keystem'],
    include_package_data=True,
    classifiers=[
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    packages=find_packages(),
    install_requires=[
        'nltk>=3.7',
        'keybert>=0.7.0',
        'spacy>=3.3.0',
        'pandas>=1.1.5',
        'numpy>=1.19.5'
        ],
    python_requires='>=3.6.0'
    
)

# https://www.freecodecamp.org/news/how-to-create-and-upload-your-first-python-package-to-pypi/
# python setup.py sdist bdist_wheel

# to build and push library 
# Change version in pyproject and setup
# python3 -m build
# twine upload --skip-existing --repository pypi dist/*
