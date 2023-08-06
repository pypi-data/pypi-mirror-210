from setuptools import setup, find_packages
setup(
    name='dbtgenlib',
    version='0.0.19',
    packages=find_packages(),
    install_requires=[
        'click',
    ],
    entry_points='''
        [console_scripts]
        yml_gen=dbtgenlib.yml_gen:dbtdocgen
        doc_gen=dbtgenlib.doc_gen:dbdoc_gen
        ''',
)