from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()


setup(name='veotos_transform',
      version='0.1.3',
      description='Obfuscate text with next consonant or vowel',
      long_description=readme(),
      classifiers=[
          'Programming Language :: Python :: 3.10',
          'Topic :: Text Processing :: Linguistic',
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)'
      ],
      url='http://github.com/veotos/veotos-transform',
      author='veotos',
      author_email='veotos@gmail.com',
      license='GPLv3',
      packages=['veotos_transform'],
      install_requires=[
          'click',
      ],
      entry_points = {
          'console_scripts': ['veotos-transform=veotos_transform.command_line:main'],
      },
      include_package_data=True,
      zip_safe=False)
