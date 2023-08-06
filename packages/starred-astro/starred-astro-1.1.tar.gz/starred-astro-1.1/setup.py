import sys
from distutils.core import setup
from setuptools.command.test import test as TestCommand

class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)

try:
    import pypandoc
    long_description = pypandoc.convert_file('README.md', 'rst')
except(IOError, ImportError):
    long_description = open('README.md').read()

setup(
    name='starred-astro',
    version='1.1',
    author='Kevin Michalewicz',
    author_email='kevinmicha@hotmail.com',
    description='A two-channel deconvolution method with Starlet regularization',
    long_description=long_description,
    packages=['starred', 'starred.deconvolution', 'starred.plots', 'starred.psf', 'starred.utils'],
    requires=['astropy', 'dill', 'galsim', 'jax', 'jaxlib', 'jaxopt', 'matplotlib', 'numpy', 'scikitimage', 'scipy', 'optax', 'tqdm'],
    cmdclass={'test': PyTest}
)
