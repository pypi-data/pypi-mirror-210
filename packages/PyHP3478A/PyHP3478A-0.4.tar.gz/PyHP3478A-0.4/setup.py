from setuptools import setup, find_packages
import json


version_file = '_INTERNAL_version.json'
project_name = 'PyHP3478A'


ver_data = json.load(open(version_file, 'r'))
local_build_version = ver_data['build']['ver']

setup(
    name=project_name,
    version=local_build_version,
    packages=find_packages(exclude=('_INTERNAL_build.py',
                                    '_INTERNAL_version.json',
                                    '.gitignore',
                                    'workspace.code-workspace')),
    url=f"https://github.com/Minu-IU3IRR/{project_name}",
    bugtrack_url = f'https://github.com/Minu-IU3IRR/{project_name}/issues',
    license='MIT',
    author='Manuel Minutello',
    description='HP3478A python interface',
    long_description=open('README.md').read(),
    install_requires=['PyAR488'],
    python_requeres = '>=3.6'
)