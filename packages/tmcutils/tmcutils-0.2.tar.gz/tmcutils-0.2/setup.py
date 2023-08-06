from setuptools import setup, find_packages


setup(
    name='tmcutils',
    version='0.2',
    license='MIT',
    author="Alessandro Orro",
    author_email='alessandro.orro@cnr.it',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='https://github.com/alessandroorro/tmcutils',
    keywords='example project',
    install_requires=[
        'pandas'
    ],

)
