import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    # ######################################################################
    # BASIC DESCRIPTION
    # ######################################################################
    name='misuma',
    author='Bang1329',
    author_email='santiago.hg2292@gmail.com',
    description='Sum two numbers',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://pypi.org/project/misuma',
    keywords='Sum Addition',
    license='MIT',

    # ######################################################################
    # CLASSIFIER
    # ######################################################################
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        ],
    version='0.6.1',

    # ######################################################################
    # FILES
    # ######################################################################
    package_dir={'': '.'},
    packages=setuptools.find_packages(where='.'),
    
    # ######################################################################
    # ENTRY POINTS
    # ######################################################################
    entry_points={
        'console_scripts': ['install=pryngles.install:main'],
    },

    # ######################################################################
    # TESTS
    # ######################################################################
    test_suite='nose.collector',
    tests_require=['nose'],

    # ######################################################################
    # DEPENDENCIES
    # ######################################################################
    install_requires=['scipy','ipython','matplotlib','tqdm'],

    # ######################################################################
    # OPTIONS
    # ######################################################################
    include_package_data=True,
    package_data={'': ['data/*.*', 'tests/*.*']},
)
