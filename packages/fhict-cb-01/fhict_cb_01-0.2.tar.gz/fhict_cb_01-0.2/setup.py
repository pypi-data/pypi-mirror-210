from setuptools import setup, find_packages


setup(
    name='fhict_cb_01',
    version='0.2',
    license='Fontys',
    author="Mark Beks et al",
    author_email='m.beks@fontys.nl',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='https://github.com/adamatei/pypi-package',
    keywords='FHICT Python support package',
    python_requires=">=3.7.0",
    install_requires=[
        'flask-login',
        'sqlalchemy',
        'flask-sqlalchemy',
        'flask>=2.0.2',
        'telemetrix'
    ],

)
