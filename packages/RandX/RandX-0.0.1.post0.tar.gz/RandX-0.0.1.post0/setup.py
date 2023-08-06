from setuptools import setup, find_packages
import os

here = os.path.abspath(os.path.dirname(__file__))

NAME = "RandX"
VERSION = '0.0.1-0'
DESCRIPTION = 'Extensible Random Number Generator'


def read(fname):
	return open(os.path.join(os.path.dirname(__file__), fname)).read()


LONG_DESCRIPTION = read("README.rst")


# Setting up
setup(
	name=NAME,
	version=VERSION,
	author="technician",
	author_email="<mail@xxxxxxxx.com>",
	description=DESCRIPTION,
	# text/plain
	# text/x-rst
	# text/markdown
	long_description_content_type="text/x-rst",
	long_description=LONG_DESCRIPTION,
	url="https://github.com/technikian/rand",
	project_urls={
		"Source": "https://github.com/technikian/rand",
	},
	license='MPL',
	license_files=["LICENSE", ],
	packages=find_packages(),
	install_requires=[],  # ['opencv-python', 'pyautogui', 'pyaudio'],
	keywords=['python', NAME, 'rand', 'random', 'number', 'generator', "extended"],
	classifiers=[
		# 1 - Planning
		# 2 - Pre-Alpha
		# 3 - Alpha
		# 4 - Beta
		# 5 - Production/Stable
		# 6 - Mature
		# 6 - Inactive
		"Development Status :: 2 - Pre-Alpha",
		"Intended Audience :: Developers",
		'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
		"Programming Language :: Python :: 3",
		'Programming Language :: Python :: 3.6',
		'Programming Language :: Python :: 3.7',
		'Programming Language :: Python :: 3.8',
		'Programming Language :: Python :: 3.9',
		'Programming Language :: Python :: 3.10',
		'Programming Language :: Python :: 3.11',
		'Operating System :: OS Independent',
		# "Operating System :: Unix",
		# "Operating System :: MacOS :: MacOS X",
		# "Operating System :: Microsoft :: Windows",
		'Topic :: Software Development :: Embedded Systems',
		"Topic :: Scientific/Engineering",
		"Topic :: Utilities",
	]
)
