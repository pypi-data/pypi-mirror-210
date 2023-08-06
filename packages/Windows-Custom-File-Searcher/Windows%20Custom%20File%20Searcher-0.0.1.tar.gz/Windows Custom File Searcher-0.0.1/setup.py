from setuptools import setup, find_packages


classifiers = [
    'Development Status :: 1 - Planning',
    'Intended Audience :: Developers',
    'Operating System :: Microsoft :: Windows :: Windows 10',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    ]

setup(
    name='Windows Custom File Searcher',
    version='0.0.1',
    description='This is a simple command line custom file searcher for windows',
    long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
    url='',
    author='Wycliffe Oloo',
    author_email='wycliflocka@gmail.com',
    license='MIT',
    classifiers=classifiers,
    keywords=['search', 'searcher', 'file', 'windows', 'custom',],
    packages=find_packages(),
    install_requires=[''],
)