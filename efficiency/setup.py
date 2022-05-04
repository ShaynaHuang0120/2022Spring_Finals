import numpy as np  # optional if not using
from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

file_name = 'py_efficiency'
ext_modules = [Extension(file_name, [f"{file_name}.pyx"]),]
# if using numpy
# ext_modules = [Extension(file_name, [f"{file_name}.pyx"], include_dirs=[np.get_include()]),]


setup(name=file_name, cmdclass={"build_ext": build_ext}, ext_modules=ext_modules)

