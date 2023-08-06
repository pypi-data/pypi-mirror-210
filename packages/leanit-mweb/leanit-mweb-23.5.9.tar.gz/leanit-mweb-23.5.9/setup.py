from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '23.5.9'
DESCRIPTION = 'Web framework'
LONG_DESCRIPTION = 'Web framework'

# Setting up
setup(
    name="leanit-mweb",
    version=VERSION,
    author="Martin Klapproth",
    author_email="martin.klapproth@staxnet.de",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=[
        'fastapi~=0.95',
        'uvicorn~=0.22',
        'uvloop~=0.17',
        'jinja2~=3.1',
        'python-multipart~=0.0',
        'wtforms~=3.0',
        'email_validator~=2.0',
        'multidict~=6.0',
        'psycopg2-yugabytedb~=2.9',
        'PyYAML~=6.0',
        'python-ulid~=1.1',
        'aiohttp~=3.7',
        # for authentication / crypto
        'bcrypt~=4.0',
        'passlib~=1.7',
        'python-jose[cryptography]~=3.3', # JWT
        # telemetry
        'opentelemetry-api~=1.18',
        'opentelemetry-sdk~=1.18',
        'opentelemetry-instrumentation-aiohttp-client~=0.39b0',
        'opentelemetry-instrumentation-fastapi~=0.39b0',
        'opentelemetry-instrumentation-logging~=0.39b0',
        'opentelemetry-exporter-otlp~=1.18',
        # for testing
        'pytest',
        'httpx',
    ],
    keywords=['python', 'web'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)