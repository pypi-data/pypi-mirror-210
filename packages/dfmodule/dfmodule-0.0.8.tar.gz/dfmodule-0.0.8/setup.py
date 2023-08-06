from setuptools import setup, find_packages

setup(
    name='dfmodule',
    version='0.0.8',
    description='data management project common features module',
    author='rimmoyee',
    author_email='rimmoyee@gmail.com',
    url='',
    install_requires=['boto3', 'b64uuid', 'cryptography', 'requests'],
    packages=find_packages(exclude=[]),
    keywords=['dfmodule', 'dfmodule777'],
    python_requires='>=3.6',
    package_data={},
    zip_safe=False,
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
)