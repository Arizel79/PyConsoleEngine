from setuptools import setup, find_packages

def readme():
  with open('README.md', 'r') as f:
    return f.read()

setup(
  name='pyAsciiEngine',
  version='0.0.1',
  author='Arizel79',
  author_email='arizel79@gmail.com',
  description='Ascii games engine',
  long_description=readme(),
  long_description_content_type='text/markdown',
  url='',
  packages=find_packages(),
  install_requires=['windows-curses==2.4.0'],
  classifiers=[
    'Programming Language :: Python :: 3.12',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent'
  ],
  keywords='ascii',
  project_urls={
    'Documentation': 'link'
  },
  python_requires='>=3.7'
)