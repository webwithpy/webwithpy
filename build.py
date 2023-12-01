from Cython.Build import build_ext, cythonize


def build(setup_kwargs: dict):
    setup_kwargs.update(
        ext_modules=cythonize(
            "webwithpy/orm/tools/cacher.pyx",
            compiler_directives={"linetrace": True},
        ),
        cmdclass={"build_ext": build_ext},
    )
