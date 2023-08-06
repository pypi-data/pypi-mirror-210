from setuptools import setup, find_packages
# import codecs
# import os
# 
# here = os.path.abspath(os.path.dirname(__file__))
# 
# with codecs.open(os.path.join(os.path.abspath(os.path.dirname(__file__)),'README.md'), encoding="utf-8") as fh:
#     long_description = "\n" + fh.read()\

from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

VERSION = '''0.10'''
DESCRIPTION = '''Uses subprocess.stdin.write and named pipes (Windows) to read data from / write data to a subprocess'''

# Setting up
setup(
    name="subprocess_multipipe",
    version=VERSION,
    license='MIT',
    url = 'https://github.com/hansalemaos/subprocess_multipipe',
    author="Johannes Fischer",
    author_email="aulasparticularesdealemaosp@gmail.com",
    description=DESCRIPTION,
long_description = long_description,
long_description_content_type="text/markdown",
    #packages=['hackyargparser', 'kthread', 'kthread_sleep', 'pywinpipe', 'subprocess_alive', 'varpickler'],
    keywords=['pickle', 'unpickle', 'subprocess'],
    classifiers=['Development Status :: 4 - Beta', 'Programming Language :: Python :: 3 :: Only', 'Programming Language :: Python :: 3.10', 'Topic :: Software Development :: Libraries :: Python Modules', 'Topic :: Utilities'],
    install_requires=['hackyargparser', 'kthread', 'kthread_sleep', 'pywinpipe', 'subprocess_alive', 'varpickler'],
    include_package_data=True
)
#python setup.py sdist bdist_wheel
#twine upload dist/*