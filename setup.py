from setuptools import setup, Extension
from Cython.Build import cythonize
import os

cython_files = ["cython_code/my_translator.pyx"]

extensions = [
    Extension(name="cython_code.my_translator", sources=["cython_code/my_translator.pyx"]),
]

setup(
    ext_modules=cythonize(extensions, build_dir="build", language_level="3"),
    package_dir={"cython_code": "cython_code"},
    packages=["cython_code"],
    zip_safe=False,
)

# python setup.py build_ext --inplace