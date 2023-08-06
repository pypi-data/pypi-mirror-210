import setuptools

readme=open("README.md").read()

setuptools.setup(
    name='simplegeomap',    
    version='0.0.22',
    description="Simple offline map plot utility, for country borders, elevation, water",
    long_description=readme,
    long_description_content_type="text/markdown",    
    install_requires=['pandas','pygeodesy','matplotlib','numpy','pyshp','scipy','zarr'],
    include_package_data=True,
    url="https://github.com/burakbayramli/simplegeomap",
    author="Burak Bayramli",
    package_data={
        "": ["*.dbf", "*.shp","*.zip","*.npz","*.csv"]
    },
    packages=setuptools.find_packages(),
 )
