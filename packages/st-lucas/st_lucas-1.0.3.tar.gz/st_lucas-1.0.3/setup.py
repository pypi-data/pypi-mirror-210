import setuptools
from st_lucas import __version__
from pathlib import Path

root_dir = Path(__file__).parent

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='st_lucas',
    version=__version__,
    description='ST_LUCAS Python package',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://gitlab.com/geoharmonizer_inea/st_lucas/st_lucas-python-package',
    packages=setuptools.find_packages(),
    package_data={
        setuptools.find_packages()[0]: [
            "logging.conf",
            "analyze/lc1_codes.csv",
            "analyze/nomenclature_translation/*"
        ]
    },
    scripts=[],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
    install_requires=[
        'geopandas>=0.8',
        'OWSLib>=0.26'
    ],
)
