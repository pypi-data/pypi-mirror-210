from setuptools import setup

setup(
    name='intra42',
    version='0.1.0',  
    description='Intra 42 utility package',
    url='https://github.com/Xentiie/py_intra42',
    author='Rémi Claire',
    author_email='reclaire@student.42mulhouse.fr',
    license='BSD 2-clause',
    packages=['intrascraper'],
    install_requires=['requests',
                      'bs4',                  
                      ],

    classifiers=[],
)
