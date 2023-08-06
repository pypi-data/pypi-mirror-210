
import setuptools

setuptools.setup(
  name = 'pyflipper',      
  package_dir={'': 'src'},
  packages=setuptools.find_packages(where='src'),
  version = '0.12',      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'Unoffical Flipper Zero cli wrapper',   # Give a short description about your library
  author = 'wh00hw',                   # Type in your name
  author_email = 'white_rabbit@autistici.org',      # Type in your E-Mail
  url = 'https://github.com/wh00hw/pyFlipper',   # Provide either the link to your github or to your website
  project_urls={
    'Documentation': 'https://github.com/wh00hw/pyFlipper/blob/master/README.md',
    'Bug Reports':
    'https://github.com/wh00hw/pyFlipper/issues',
    'Source Code': 'https://github.com/wh00hw/pyFlipper',
  },
  keywords = ['flipper', 'wrapper', 'module'],   # Keywords that define your package best
  install_requires=[
          'pyserial',
          'websocket-client',
      ],
  classifiers=[
    # see https://pypi.org/classifiers/
    'Development Status :: 4 - Beta',

    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',

    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
 ],
  python_requires='>=3.8',
)