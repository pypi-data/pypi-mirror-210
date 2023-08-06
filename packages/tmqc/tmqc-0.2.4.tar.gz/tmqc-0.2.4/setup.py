import setuptools

# 第三方依赖包及版本
requires = [
    'aiohttp',
    'akshare',
    'beautifulsoup4',
    'better_exceptions',
    'chardet',
    'colorama',
    # '#Cython>=3.0.0a10',
    'demjson',
    'easyutils',
    'grpcio',
    'httpx',
    'matplotlib',
    'mysql_connector_repackaged',
    'mysql-connector-python',
    'numpy',
    'pandas',
    'protobuf',
    'psutil',
    'pycryptodome',
    'pymongo',
    'PyMySQL',
    'python_dateutil',
    'redis',
    'requests',
    'scipy',
    'stompest',
    'Twisted',
    'urllib3',
    'xlrd',
    'yarl'
]

with open("README.md", "r") as fh:
    long_description = fh.read()
    
setuptools.setup(name='tmqc',
    version='0.2.4',
    description='tian ma quant cloud',
    author='tmqc',
    author_email='tmqc@gmail.com',
    url="https://github.com/tmqc/tmqc",
    license='LGPT',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    python_requires='>=3.7',
    install_requires = requires,
    include_package_data=True,
    zip_safe=False)