import re
from pathlib import Path
from setuptools import find_packages, setup


def get_version() -> str:
    file = Path("src/cenao/version.py")
    content = file.read_text(encoding="utf-8")

    m = re.search(r'^\s*__version__\s*\=\s*[\'"]([^\'""]+)[\'"]', content, re.M)
    assert m
    return m.group(1)


setup(
    name='cenao',
    version=get_version(),
    url='https://gitlab.uwtech.org/uwtech/cenao',
    license='MIT',
    author='Roman Shishkin',
    author_email='spark@uwtech.org',
    description='Python framework for fast and async applications',
    project_urls={
        'Source': 'https://gitlab.uwtech.org/uwtech/cenao',
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Framework :: AsyncIO",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Internet :: WWW/HTTP",
    ],
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    python_requires='>=3.8',
    install_requires=[
        'aiohttp>=3.8.4',
        'async-timeout==4.0.2',
        'PyYAML==6.0',
        'prometheus_client==0.14.1',
        'uvloop>=0.16.0 ; sys_platform != \'win32\'',
    ],
    extras_require={
        'redis': [
            'aioredis>=1.3.1, <1.4.0',
            'aioredis-cluster>=2.4.0, <3.0',
        ],
    }
)
