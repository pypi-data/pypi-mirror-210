#!/usr/bin/env python3

import codecs
from os import path
from setuptools import setup

pwd = path.abspath(path.dirname(__file__))
with codecs.open(path.join(pwd, 'README.md'), 'r', encoding='utf8') as input:
    long_description = input.read()

version='1.18'
	
setup(
	name='HaversineAPI',
	version=version,
	license='MIT',
    long_description=long_description,
	long_description_content_type="text/markdown",
	url='https://github.com/eddo888/HaversineAPI',
	download_url='https://github.com/eddo888/HaversineAPI/archive/%s.tar.gz'%version,
	author='David Edson',
	author_email='eddo888@tpg.com.au',
	packages=[
		'Haversine',
	],
	install_requires=[
		'dotmap',
		'tqdm',
		'pygeohash',
		'Baubles',
		'Perdy',
		'Argumental',
	],
	scripts=[
		"Haversine/haversine.py",
		"Haversine/haversine.sh",
	],
)
