import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    # ######################################################################
    # BASIC DESCRIPTION
    # ######################################################################
    name='miresta',
    author='Diana Carolina Zapata Zuluaga',
    author_email='dianac.zapata@udea.edu.co',
    description='This package performs a subtraction',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://pypi.org/project/miresta',
    keywords='subtraction',
    license='MIT',

    # ######################################################################
    # CLASSIFIER
    # ######################################################################
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        ],
    version='0.7',

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
    install_requires=['numpy'],

    # ######################################################################
    # OPTIONS
    # ######################################################################
    include_package_data=True,
    package_data={'': ['data/*.*', 'tests/*.*']},
)
