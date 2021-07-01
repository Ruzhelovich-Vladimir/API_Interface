# coding: utf-8

from cx_Freeze import setup, Executable
import os

build_exe = os.path.join(os.curdir, 'build_exe')

try:
    os.mkdir(build_exe)
except:
    pass
#

base = 'win32' #'win32' #

executables = [
            Executable('api_module.py' ),
            Executable('json_converter_module.py'),
            Executable('to_zip_media.py'),
            Executable('main_console_module.py'),
            Executable('main_module.py')
               ]

excludes = []
#['asyncio','concurrent','ctypes','distutils','lib2to3','multiprocessing','pydoc_data','test','tkinter','unittest','xml','xmlrpc']

zip_include_packages = ["*"]

#'html'
#                        'bs4',
#                        'lxml',
#                        'soupsieve',
#                        'select',
#                        'unicodedata',
#                        'certifi',
#                        'chardet',
#                        'collections',
#                        'email',
#                        'encodings',
#                        'http',
#                        'idna',
#                        'importlib',
#                        'json',
#                        'logging',
#                        'requests',
#                        'urllib',
#                        'urllib3',
#			'_distutils_hack',
#			'asyncio',
#			'certifi',
#			'chardet',
#			'collections',
#			'concurrent',
#			'config',
#			'ctypes',
#			'distutils',
#			'dynaconf',
#			'email',
#			'encodings',
#			'html',
#			'http',
#			'idna', 
#			'importlib',
#			'json',
#			'lib2to3',
#			'logger',
#			'logging',
#			'msilib',
#			'multiprocessing',
#			'pip',
#			'pkg_resources',
#			'pydoc_data',
#			'requests',
#			'setuptools',
#			'test',
#			'tkinter',
#			'unittest',
#			'urllib',
#			'urllib3',
#			'xml',
#			'xmlrpc',
#			'_asyncio.pyd',
#			'_bz2.pyd',
#			'_ctypes.pyd',
#			'_decimal.pyd',
#			'_elementtree.pyd',
#			'_hashlib.pyd',
#			'_lzma.pyd',
#			'_msi.pyd',
#			'_multiprocessing',
#			'_overlapped',
#			'_queue',
#			'_socket',
#			'_ssl',
#			'_testcapi',
#			'_tkinter',
#			'pyexpat',
#			'select',
#			'unicodedata'

includes = ["os","dynaconf","zipfile","sys","logging","json","sys","csv","http.client","ssl","requests","shutil"]

# "queue",
#             "os",
#             "requests",
#             "http.client",
#             "json",
#             "dynaconf",
#             "encodings",
#             "logger"

packages = ["os","zipfile","sys","logging","json","sys","csv","http.client","ssl","requests","shutil"]

# "os", "requests","http.client","json","dynaconf","logger"
#        'excludes': excludes,
#       'zip_include_packages': zip_include_packages,
#        'packages': packages,


options = {
    'build_exe': {
        'include_msvcr': True,
        'includes': includes,
	    'build_exe': build_exe,
        'optimize':1
	}
}

setup(name='API Interface', version='1.0', description='API Interface', executables=executables, options=options)
