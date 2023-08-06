from setuptools import setup, find_packages
setup(
    name='dbtgenlib',
    version='0.0.22',
    packages=find_packages(),
    install_requires=[
        'click',
    ],
    entry_points='''
        [console_scripts]
        genyml=dbtgenlib.yml_gen:dbtdocgen
        gendoc=dbtgenlib.doc_gen:dbdoc_gen
        testkeys=test.test_keys:check_skeys
        ''',
)