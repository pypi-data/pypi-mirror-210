from setuptools import setup, find_packages
import json


version_file = '_INTERNAL_version.json'
project_name = 'PyRigol_DS1000x'
external_modules = ('pyvisa')

ver_data = json.load(open(version_file, 'r'))
local_build_version = ver_data['build']['ver']

setup(
    name=project_name,
    version=local_build_version,
    packages=find_packages(exclude=('_INTERNAL_build.py',
                                    '_INTERNAL_version.json',
                                    '.gitignore',
                                    'workspace.code-workspace')),
    url="https://github.com/Minu-IU3IRR/PyRigol_DS1000x",
    bugtrack_url = 'https://github.com/Minu-IU3IRR/PyRigol_DS1000x/issues',
    license='MIT',
    author='Manuel Minutello',
    description='module to easily contorl a Rigol DS1000x series scope and quickly build a measurement setup',
    long_description=open('README.md').read(),
    install_requires=external_modules,
    python_requeres = '>=3.6'
)