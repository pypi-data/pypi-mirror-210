from setuptools import setup, find_packages
 
classifiers = [
  'Operating System :: OS Independent',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
  name='CEEcache',
  version='1.0.2',
  description='Caching the JSON request payload and the value in RedisQ',
  long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
  url='',  
  author='Netcore Cloud',
  author_email='aditya.singh@netcorecloud.com',
  license='MIT', 
  classifiers=classifiers,
  packages=find_packages(),
  install_requires=['redis==4.5.5','fluent-logger==0.9.6','requests'] 
)