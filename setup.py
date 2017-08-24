from setuptools import setup
setup(name='shatag',
      version = '0.5.0',
      description = 'File checksumming utility',
      author = 'Maxime Augier',
      author_email = 'max@xolus.net',
      url = 'http://bitbucket.org/maugier/shatag',
      packages = ['shatag','shatag.backend','shatag.store','shatag.cli'],
      install_requires=['pyyaml','xattr','pyinotify'],
      entry_points={
          'console_scripts': [
              'shatag = shatag.cli.shatag:main',
              'shatag-add = shatag.cli.add:main',
              'shatagd = shatag.cli.shatagd:main'
          ]
      }
)
