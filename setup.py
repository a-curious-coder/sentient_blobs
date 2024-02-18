import os

from setuptools import find_packages, setup


def read_requirements():
   reqs = []
   if os.path.exists("requirements.txt"):
       with open("requirements.txt") as f:
           reqs = f.read().splitlines()
   return reqs

setup(
  name='Sentient_Blobs',
  version='0.1',
  packages=find_packages(),
#   url='http://your-package-url.com',
  license='MIT License',
  author='Curious Coder',
#   author_email='your.email@example.com',
  description='Description of your package',
  long_description=open('README.md').read(),
  install_requires=read_requirements(),
)
