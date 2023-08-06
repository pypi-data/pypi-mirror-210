import io
from os.path import abspath, dirname, join
from setuptools import find_packages, setup


HERE = dirname(abspath(__file__))
LOAD_TEXT = lambda name: io.open(join(HERE, name), encoding='UTF-8').read()
DESCRIPTION = '\n\n'.join(LOAD_TEXT(_) for _ in [
    'README.rst'
])

setup(
  name = 'paotung',      
  packages = ['paotung'], 
  version = '0.0.1', 
  license='MIT', 
  description = 'Who is Paotung',
  long_description=DESCRIPTION,
  author = 'Patcharaporn',                 
  author_email = 'patcharaporn.online63@gmail.com',     
  url = 'https://github.com/Patcharaporn2093',  
  download_url = 'https://github.com/Patcharaporn2093',  
  keywords = ['Paotung', 'ASCII ART', 'Cat'],
  classifiers=[
    'Development Status :: 3 - Alpha',     
    'Intended Audience :: Education',     
    'Topic :: Utilities',
    'License :: OSI Approved :: MIT License',   
    'Programming Language :: Python :: 3',      
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
  ],
)