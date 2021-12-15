from distutils.core import setup
from Cython.Build import cythonize

dirPath = {{files}}

setup(ext_modules=cythonize(dirPath, compiler_directives={'language_level': "3"}))
