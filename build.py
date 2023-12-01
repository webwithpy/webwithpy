from setuptools import setup
from Cython.Build import cythonize
from distutils.command.build_ext import build_ext

setup(
    name="cacher",
    ext_modules=cythonize(
        "webwithpy/orm/tools/cacher.pyx", compiler_directives={"linetrace": True}
    ),
    cmdclass={"build_ext": build_ext},
)
