from setuptools import setup
import subprocess

def get_version():
    try:
        return subprocess.check_output(['git', 'describe', '--tags', '--always']).strip().decode("utf-8")
    except:
        return "0.0.dev0"

setup(
    name='scrapy-url-frontier',
    version=get_version(),
    author='Andrew N. Jackson',
    author_email='anj@anjackson.net',
    packages=['urlfrontier'],
    package_data={'urlfrontier': ['grpc/urlfrontier.proto']},
    #url='http://pypi.python.org/pypi/scrapy-url-frontier/',
    license='LICENSE.txt',
    description='Scrapy module for the Crawler Commons URL Frontier.',
    long_description=open('README.md').read(),
    install_requires=[
        "scrapy",
        "uhashring",
        "grpcio",
    ],
    # Additional dependencies for development or use of Frontera classes:
    extras_require={
        'dev': [ 'pytest','grpcio-tools' ],
        'frontera': [ 'frontera' ]
    },
    entry_points={
        'console_scripts': [
            'scrapy-url-frontier=urlfrontier.cmd:main',
        ]
    }
)