from setuptools import setup, Extension
from Cython.Build import cythonize

extensions = [
    Extension(name="cython_code.my_translator", sources=["cython_code/my_translator.pyx"]),
    Extension(name="cython_code.user_check", sources=["cython_code/user_check.pyx"]),
    Extension(name="cython_code.throttling_middleware", sources=["cython_code/throttling_middleware.pyx"]),
    Extension(name="cython_code.file_db", sources=["cython_code/file_db.pyx"]),
    Extension(name="cython_code.send_ads", sources=["cython_code/send_ads.pyx"]),  # Corrected
]

setup(
    ext_modules=cythonize(extensions, build_dir="build", language_level="3"),
    package_dir={"cython_code": "cython_code"},
    packages=["cython_code"],
    zip_safe=False,
)



# python setup.py build_ext --inplace