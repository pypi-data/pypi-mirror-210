from setuptools import setup, find_packages
setup(
    name='dbtgenlib',
    version='0.0.20',
    packages=find_packages(),
    install_requires=[
        'click',
    ],
    entry_points='''
        [console_scripts]
        genyml=dbtgenlib.yml_gen
        doc_gen=dbtgenlib.doc_gen:dbdoc_gen
        ''',
)