from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.readlines()

long_description = 'Command line program to fix okn and pim related issues.'

setup(
    name='oknpatch',
    version='3.0.0',
    author='Zaw Lin Tun',
    author_email='zawlintun1511@gmail.com',
    url='https://github.com/jtur044/oknpatch',
    description='issues fixing program',
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="Apache Software",
    packages=find_packages(),
    include_package_data=True,
    package_data={'': ['gazefilters.json', 'okndetector.gaze.config']},
    entry_points={
        'console_scripts': [
            'oknpatch = oknpatch.oknpatch:main'
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    keywords='oknpatch',
    install_requires=requirements,
    zip_safe=False
)
