import glob
import os
from setuptools import setup, find_packages

install_requires = [line.rstrip() for line in open(os.path.join(os.path.dirname(__file__), "requirements.txt"))]

setup(name='dcp-diag',
      version='0.6.0',
      description='Data Coordination Platform diagnostic library and tools.',
      url='http://github.com/HumanCellAtlas/dcp-diag',
      author='Sam Pierson',
      author_email='spierson@chanzuckerberg.com',
      license='MIT',
      packages=find_packages(exclude=['tests']),
      scripts=glob.glob('scripts/*'),
      zip_safe=False,
      install_requires=install_requires,
      platforms=['MacOS X', 'Posix'],
      test_suite='test',
      classifiers=[
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: POSIX',
          'Programming Language :: Python :: 3.6'
      ]
      )
