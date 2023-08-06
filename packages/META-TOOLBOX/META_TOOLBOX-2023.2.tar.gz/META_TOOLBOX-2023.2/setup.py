from setuptools import setup

setup(
    	name = 'META_TOOLBOX',
    	version = '2023.2',
		url = 'https://wmpjrufg.github.io/META_TOOLBOX/',
    	license = 'Apache License',
    	author_email = 'wanderlei_junior@ufcat.edu.br',
    	packages = ['META_TOOLBOX'],
    	description = "The METApy optimization toolbox is an easy of use environment for applying metaheuristic optimization methods. The platform has several optimization methods, as well as functions for generating charts and statistical analysis of the results.",
    	classifiers = ["Programming Language :: Python","Topic :: Scientific/Engineering :: Mathematics", "Topic :: Scientific/Engineering"],
    	install_requires = ["Numpy", "Xlsxwriter", "pandas"]
    )

