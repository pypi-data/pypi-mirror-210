from distutils.core import setup, Extension

module = Extension("ElGamal_c", sources=["encryptmodule.c"]
                  #  ,extra_compile_args=['/openmp']
                   )

long_description =\
"""
This module have been made for the project of discret math CSC281 at ksu university.
The project supervisor is Aqil Alazimi. LinkedIn: https://www.linkedin.com/in/aqil-azmi-20903960/
The project repo is: https://github.com/Wouze/csc281-project
"""

setup(name="ElGamal_c",
      version="1.0.1",
      author="Wouze (Mohammad)",
      author_email="m7mdwats1@hotmail.com",
      description="This module is for csc281 encryption project ",
      long_description_content_type="text/markdown",
      long_description=long_description,
      url='https://github.com/Wouze/csc281-project',
      keywords=['python', 'c', 'primitive root', 'encryption', 'algamal', 'prime'],
      classifiers=[
            "Development Status :: 1 - Planning",
            "Intended Audience :: Developers",
            "Programming Language :: Python :: 3",
            "Operating System :: Unix",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
      ],
      ext_modules=[module])

