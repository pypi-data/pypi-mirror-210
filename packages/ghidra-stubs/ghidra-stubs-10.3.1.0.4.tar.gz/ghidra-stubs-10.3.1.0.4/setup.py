
from setuptools import setup
import os

def find_stub_files():
    result = []
    package = 'ghidra-stubs'
    for root, dirs, files in os.walk(package):
        for file in files:
            if file.endswith('.pyi'):
                file = os.path.relpath(os.path.join(root,file), start=package)
                result.append(file)
    return result

setup(name= 'ghidra-stubs',
version='10.3.1.0.4',
author='Tamir Bahar',
packages=['ghidra-stubs'],
url="https://github.com/VDOO-Connected-Trust/ghidra-pyi-generator",
package_data={'ghidra-stubs': find_stub_files()})
    