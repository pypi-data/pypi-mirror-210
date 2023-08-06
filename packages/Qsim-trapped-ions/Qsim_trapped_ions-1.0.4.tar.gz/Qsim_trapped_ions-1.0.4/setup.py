# -*- coding: utf-8 -*-
"""
Created on Tue May 23 14:37:08 2023

@author: zhumj
"""

from setuptools import setup

def readme_file():
    with open(".\\Qsim\\README.rst") as rf:
        return rf.read()
    
setup(name = 'Qsim_trapped_ions', 
      version = '1.0.4', 
      description = 'Numerical simulation of trapped ion quantum dynamics',
      package_dir = {
            'Qsim': 'Qsim',
            'Qsim.ion_chain': 'Qsim/ion_chain',
            'Qsim.operator': 'Qsim/operator',
            'Qsim.ion_chain.eigendiagram': 'Qsim/ion_chain/eigendiagram',
            'Qsim.ion_chain.interaction': 'Qsim/ion_chain/interaction',
            'Qsim.ion_chain.ising': 'Qsim/ion_chain/ising',
            'Qsim.ion_chain.transfer': 'Qsim/ion_chain/transfer',},
      install_requires=[
          'qutip'],
      packages = ['Qsim.ion_chain','Qsim.operator','Qsim.ion_chain.eigendiagram','Qsim.ion_chain.interaction',
                  'Qsim.ion_chain.ising', 'Qsim.ion_chain.transfer',],
      author = 'Mingjian Zhu',
      author_email='mz40@rice.edu',
      long_description = readme_file(),
      url = 'https://github.com/TrappedIonRice/Open-Quantum-system-simulation')