from setuptools import setup, find_packages


setup(
    name='indicopicture',
    version='0.1',
    author='Claudio Morgia',
    author_email='cmorgia@unog.ch',
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'indico>=1.9.1',
    ],
    entry_points={'indico.plugins': {'indicopicture = indicopicture:IndicoPicturePlugin'}}
)
