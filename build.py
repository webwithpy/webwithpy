from setuptools import setup
from Cython.Build import cythonize

setup(
    name='cacher',
    ext_modules=cythonize("webwithpy/orm/tools/cacher.pyx"),
)
