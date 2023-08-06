from setuptools import setup, find_packages

setup(
    # Needed to silence warnings (and to be a worthwhile package)
    name='solver4mpi',
    url='https://github.com/mathias77515/optimized_minimizer',
    author='Mathias Regnier',
    author_email='mathias.p.regnier@gmail.com',
    # Needed to actually package something
    packages=find_packages(),
    # Needed for dependencies
    install_requires=[],
    # *strongly* suggested for sharing
    version='1.2',
    # The license can be anything you like
    license='',
    description='Optimized minimizer for MPI python.',
    # We will also need a readme eventually (there will be a warning)
    # long_description=open('README.txt').read(),
)
