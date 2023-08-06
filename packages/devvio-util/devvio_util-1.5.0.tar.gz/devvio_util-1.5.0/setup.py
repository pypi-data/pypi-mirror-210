from setuptools import setup

setup(name='devvio_util',
      version='1.5.0',
      long_description=open('README.txt').read(),
      long_description_content_type='text/markdown',
      description='Utility to be used inside Devvio projects',
      author='Mateus Sens',
      author_email='mateus.sens@tarmac.io',
      license='Devvio',
      packages=['devvio_util', 'devvio_util/primitives'],
      zip_safe=False
)
