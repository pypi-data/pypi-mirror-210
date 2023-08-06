from setuptools import setup

setup(
    name='dbuse',
    version='1.0.0',
    description='Una clase para acceder a MySQL',
    long_description='Una clase para acceder a MySQL, con métodos diseñados para facilitar la conexión, la ejecución de consultas y la destrucción del cursor cuando ya no sea necesario.',
    url='https://github.com/josequijado/python_DBAccess',
    author='José Quijado',
    author_email='jquijado@gmail.com',
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3.8',
    ],
    keywords='MySQL, Python, clase',
    packages=['dbuse'],
    install_requires=[
        'mysql.connector',
    ],
)
