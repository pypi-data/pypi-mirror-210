"""
Kolibri
An elegant static site generator
"""

import os
from setuptools import setup, find_packages


base_dir = os.path.dirname(__file__)

__about__ = {}
__install_requires = []

with open(os.path.join(base_dir, "src", "ssg", "__about__.py")) as f:
    exec(f.read(), __about__)

with open("requirements.txt") as f:
    __install_requires = f.read().splitlines()


setup(
    name="ssgpy",
    version=__about__["__version__"],
    license=__about__["__license__"],
    author=__about__["__author__"],
    author_email=__about__["__email__"],
    description=__about__["__summary__"],
    url=__about__["__uri__"],
    long_description=__about__["__long_description__"],
    py_modules=['ssg'],
    python_requires='>=3.8.0',
    entry_points=dict(console_scripts=[
        'ssg=ssg.cli:cmd'
    ]),
    include_package_data=True,
    packages=['ssg'],
    install_requires=__install_requires,
    package_dir={'':'src'},
    keywords=['static site generator'],
    platforms='any',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    zip_safe=False
)
