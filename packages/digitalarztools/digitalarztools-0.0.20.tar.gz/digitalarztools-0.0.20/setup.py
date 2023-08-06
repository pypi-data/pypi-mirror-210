import setuptools

"""
to create pip package
install twine
pip install twine 
python setup.py sdist bdist_wheel
twine upload dist/* 
"""
import os

lib_folder = os.path.dirname(os.path.realpath(__file__))
requirement_path = os.path.join(lib_folder, 'requirements.txt') #lib_folder + '/digitalarztools/requirements.txt'
install_requires = []  # Here we'll get: ["gunicorn", "docutils>=0.3", "lxml==0.5a7"]
if os.path.isfile(requirement_path):
    with open(requirement_path) as f:
        install_requires = f.read().splitlines()

VERSION = '0.0.20'
DESCRIPTION = 'Digital Arz tools for applications'
LONG_DESCRIPTION = 'Package provides tool for developing digitalarz application using rasterio, gdal, geopandas, and pandas'

# Setting up
setuptools.setup(
    name="digitalarztools",
    version=VERSION,
    author="Ather Ashraf",
    author_email="atherashraf@gmail.com",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,

    install_requires=install_requires,  # add any additional packages that
    # needs to be installed along with your package. Eg: 'caer'
    setup_requires=install_requires,
    packages=setuptools.find_packages(),
    keywords=['raster', 'vector', 'digitalarz'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Education",
        "Programming Language :: Python :: 3",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)

print(install_requires)
