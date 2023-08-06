from setuptools import setup, find_packages
setup(
    name='dbtgenlib',
    version='0.0.26',
    packages=find_packages(),
    install_requires=[
        'click',
    ],
    entry_points='''
        [console_scripts]
        genyml=dbtgenlib.genyml:dbtdocgen
        gendoc=dbtgenlib.gendoc:dbdoc_gen
        testkeys=tests.test_keys:check_skeys
        ''',
)