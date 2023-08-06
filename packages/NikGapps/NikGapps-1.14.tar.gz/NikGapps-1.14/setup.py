from setuptools import setup, find_packages

setup(
    name="NikGapps",
version="1.14",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        '': ['*.sh', '*.yml'],
        'NikGapps.helper': ['assets/*'],
        'NikGapps.helper.assets': ['*'],
    },
    author="Nikhil Menghani",
    author_email="nikgapps@gmail.com",
    description="A short description of your project",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/nikgapps/project",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires='>=3.10',
)
