from setuptools import setup, find_packages

version = '1.0'
with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(name='Arproof',
      version=version,
      description="A front-end cli-app utility for Tuxcut's daemon",
      long_description="""\
Since tuxcut gui is broken, I wrote a python script that will communicate from it's daemon which is the core program of tuxcut""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='ArpSpoof',
      author='2k16daniel',
      author_email='2k16daniel@gmail.com',
      url='',
      license='MIT',
      package_dir={'':'./'},
      packages=(
        find_packages() +
        find_packages('arproof')+
        find_packages('server')
      ),
      include_package_data=True,
      zip_safe=True,
      install_requires=required,
      entry_points={
            'console_scripts': [
                'arproof = arproof.arproof:main',
                'tuxcutd = server.tuxcutd:isOnRootPrivilege',
            ],
        },
      )
