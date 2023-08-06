from setuptools import setup, find_namespace_packages

packagereqs = ['sendgrid', 'plyer', 'pygame', 'pandas', 'google-auth', 'google-auth-oauthlib', 'google-auth-httplib2', 'google-api-python-client', 'Pillow', 'Scipy', 'Numpy']

with open('README.txt', 'r') as fh:
    long_description = fh.read()

setup(
    name='JBPhD',
    version='2.2.2',
    packages=find_namespace_packages(include=['Task']),
    install_requires=packagereqs,
    entry_points={
        'console_scripts': [
            'myproject = myproject.main:main'
        ]
    },
    description=long_description,
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    include_package_data=True,
    data_files=[('.', ['README.txt', 'MANIFEST.in'])],
)
