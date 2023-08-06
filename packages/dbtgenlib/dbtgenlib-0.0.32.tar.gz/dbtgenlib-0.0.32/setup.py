from setuptools import setup, find_packages
setup(
    name='dbtgenlib',
    version='0.0.32',
    packages=find_packages(),
    install_requires=[
        'click',
    ],
    entry_points='''
        [console_scripts]
        yml_gen=dbtgenlib.genyml:dbtdocgen
        doc_gen=dbtgenlib.gendoc:dbdoc_gen
        key_test=dbtgenlib.testkeys:check_skeys
        ''',
)