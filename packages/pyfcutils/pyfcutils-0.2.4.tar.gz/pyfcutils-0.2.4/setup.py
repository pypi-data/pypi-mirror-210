import platform as pltf
from sys import platform

import numpy
from Cython.Build import cythonize
from setuptools import setup
from setuptools.extension import Extension

fcio_libs = 'src/libs'

if platform.startswith('freebsd') or platform.startswith('linux'):
    extra_objects = [f'{fcio_libs}/fcio_linux.a', f'{fcio_libs}/tmio-0.93_linux.a']
elif platform.startswith('darwin'):
    if pltf.processor() == 'i386':
        print('Using macOS intel static library')
        extra_objects = [f'{fcio_libs}/fcio_mac.a', f'{fcio_libs}/tmio-0.93_mac.a']
    elif pltf.processor() == 'arm':
        extra_objects = [
            f'{fcio_libs}/fcio_mac_arm.a',
            f'{fcio_libs}/tmio-0.93_mac_arm.a',
        ]
        print('Using macOS arm static library')
elif platform.startswith('win32'):
    raise Exception('Windows not supported!')

extensions = [
    Extension(
        'fcutils',
        sources=['src/fcutils/fcutils.pyx'],
        include_dirs=[fcio_libs, 'src/fcutils', numpy.get_include()],
        extra_objects=extra_objects,
    )
]


extensions = cythonize(extensions, language_level=3)

setup(ext_modules=extensions)
