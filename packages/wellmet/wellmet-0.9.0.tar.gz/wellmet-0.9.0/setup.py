from setuptools import setup, find_packages

VERSION = '0.9.0' 
DESCRIPTION = 'a pure Python framework for spatial structural reliability analysis'
LONG_DESCRIPTION = "WellMet is a pure Python framework for failure probability estimation and detection of failure surfaces by adaptive sequential decomposition of the design domain"

# Setting up
setup(
       # the name must match the folder name 'verysimplemodule'
        name="wellmet",
        version=VERSION,
        author="Gerasimov Aleksei",
        author_email="<ger-alex@seznam.cz>",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        url="https://rocketgit.com/iam-git/WellMet",
        license="MIT",
        install_requires=[
		  "numpy",
		  "scipy",
		  "mpmath",
		  "quadpy",
		  "pandas",
		  "PyQt5",
		  "pyqtgraph>=0.13.1",
		],
        
        keywords=['failure probability', 'Monte Carlo', 'surrogate model'],
        classifiers = [
			"Topic :: Scientific/Engineering",
		    "Intended Audience :: Science/Research",
		    "Programming Language :: Python :: 3",
		    "License :: OSI Approved :: MIT License",
		    "Operating System :: OS Independent",
		]
)

