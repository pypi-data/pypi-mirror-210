from setuptools import setup, find_packages

classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'Operating System :: Microsoft :: Windows :: Windows 8.1',
  'Operating System :: Microsoft :: Windows :: Windows 8',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]

setup(
  name='vtrans',
  version='2.0.0',
  description='This is a self-updating translator powered by Google Translate for free and unlimited usage.',
  long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
  url='https://github.com/megalosVigneswaran/vtrans/tree/main/vtrans',  
  author='S.Vigneswaran',
  author_email='t896242@gmail.com',
  license='MIT',
  classifiers=classifiers,
  keywords=['translator', 'googletranslate', 'self-updating', 'googletrans'],
  packages=find_packages(),
  package_data={
        'vtrans': ['config.txt'],
    },
  install_requires=['googletrans==3.1.0a0', 'pandas', 'requests', 'beautifulsoup4', 'astor'] 
)
