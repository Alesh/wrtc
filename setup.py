from setuptools import setup, find_packages

setup(**{
    'name': 'Sample OTApp',
    'packages': find_packages(),
    'install_requires': [
        'aiohttp>=3.6.2',
        'opentok>=2.10.0'
    ],
})