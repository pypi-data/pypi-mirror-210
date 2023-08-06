from setuptools import setup
import os
valueVersion = os.getenv('GITHUB_REF_NAME')
setup(name='packagetestbancolombia',
version=valueVersion,
description='Testing installation of Package',
url='https://github.com/bancolombia/test-distribute-pypi',
author='ghoyos',
author_email='ghoyos@bancolombia.com.co',
license='MIT',
packages=['packagetestbancolombia'],
zip_safe=False)