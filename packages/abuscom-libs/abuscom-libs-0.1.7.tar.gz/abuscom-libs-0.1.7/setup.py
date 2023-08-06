from setuptools import setup

setup(
    name='abuscom-libs',
    version='0.1.7',
    description='Utility classes for airflow DAGs',
    url='https://abuscom.com',
    author='Leonhard Holzer',
    author_email='leonhard.holzer@abuscom.com',
    license='BSD 2-clause',
    packages=['abuscom.connectors'],
    install_requires=['apache-airflow>=2.4.3',
                      'pandas',
                      ],

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: Freeware',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.8',
    ],
)