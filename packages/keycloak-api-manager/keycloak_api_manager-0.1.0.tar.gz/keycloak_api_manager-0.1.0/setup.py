from setuptools import setup
setup(
   name='keycloak_api_manager',
   version='0.1.0',
   author='Polyakov Sergey',
   author_email='martinlauren555@gmail.com',
   packages=['keycloak_api_manager'],
   url='',
   license='LICENSE.txt',
   description='API for Keycloak management',
   long_description='API for Keycloak management',
   install_requires=[
       "requests"
   ])