from setuptools import setup,find_packages


import os
here = os.path.abspath(os.path.dirname(__file__))
readme = open(os.path.join(here, 'README.md'), 'r').read()
changelog = open(os.path.join(here, 'CHANGELOG.md'), 'r').read()

setup(name='config2sqlalchemy',
  version='0.0.1',
  description='create a sqlalchemymodel from json configuration',
  long_description=readme + "\n\n\n" + changelog,
  long_description_content_type="text/markdown",
  author='pdepmcp',
  author_email='pdepmcp@gmail.com',
  license='MIT',
  classifiers=[
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'Operating System :: OS Independent',
    'Framework :: Pyramid',
    
    'Programming Language :: Python :: 3.6',
  ],
  keywords="pyramid module sqlalchemy model",
  python_requires='>=3.6',
  url='http://www.pingpongstars.it',
  install_requires=['sqlalchemy','pyramid>=1.1' ],
  #packages=['src/test1'],
  packages=find_packages(),
  include_package_data=True,

)


