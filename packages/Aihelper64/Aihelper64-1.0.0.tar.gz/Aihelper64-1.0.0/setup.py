from setuptools import setup, find_packages

def readme():
  with open('README.txt', 'r') as f:
    return f.read()

setup(
  name='Aihelper64',
  version='1.0.0',
  author='Limonchik228005',
  author_email='bad228005@gmail.com',
  description='This is my first module, to help using OpenAi API',
  long_description=readme(),
  long_description_content_type='text/markdown',
  url='https://github.com/artem228005/Aihelper',
  packages=find_packages(),
  install_requires=['requests>=2.25.1'],
  classifiers=[
    'Programming Language :: Python :: 3.11',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent'
  ],
  keywords='example python',
  project_urls={
    'Documentation': "https://github.com/artem228005/Aihelper"
  },
  python_requires='>=3.7'
)