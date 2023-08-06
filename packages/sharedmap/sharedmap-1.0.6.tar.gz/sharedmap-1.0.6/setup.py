import sys
from setuptools import setup,Extension,find_packages
version = sys.version_info

projname = "sharedmap"



module1 = None;

other_sources = [
	"native/stringbox.cpp",
	"native/tree.cpp",
	"native/avltree.cpp",
	"native/rbtree.cpp",
	"native/pyshareabledict.cpp",
	"native/pysharedbitmap.cpp",
	"native/pyrbtree.cpp",
	"native/pynative.cpp",
]

include_files = [
	"native/avltree.h",
	"native/pynative.h",
	"native/pytree.h",
	"native/rbtree.h",
	"native/stringbox.h",
	"native/tree.h",
]

if version >= (2,0) and version < (3,0):
	module1 = Extension('sharedmap',sources = other_sources,include_dirs=['./native'],libraries = ['rt'],extra_compile_args=["-DNDEBUG"],extra_link_args=["-s"])
elif version >= (3,0) and version < (4,0):
	module1 = Extension('sharedmap',sources = other_sources,include_dirs=['./native'],libraries = ['rt'],extra_compile_args=["-DNDEBUG"],extra_link_args=["-s"])



try:
	with open("README.md", "r") as fh:
		long_description = fh.read()
except Exception as e:
	long_description = "";


setup (name = projname,
	version = '1.0.6',
	description = projname,
	long_description=long_description,
	long_description_content_type="text/markdown",
	author = "lyramilk",
	packages=[],
	ext_modules = [module1],
	data_files=include_files,
	install_requires = [],
	author_email='lyramilk@qq.com',
	license='Apache License 2.0',
	url='', 
	classifiers=[
		"Intended Audience :: Developers",
		"Operating System :: OS Independent",
		"Natural Language :: Chinese (Simplified)",
		'Programming Language :: Python',
		'Programming Language :: Python :: 3',
		'Topic :: Utilities'
	],
	keywords = 'sharedmap,sharememory,rbtree,avltree',
)

