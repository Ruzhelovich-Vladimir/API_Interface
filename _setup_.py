# coding: utf-8

from cx_Freeze import setup, Executable
import os

build_exe = os.path.join(os.curdir, 'build_exe')

try:
    os.mkdir(build_exe)
except:
    pass


base = 'Win32GUI' #'win32' #

executables = [
            Executable('api_module.py', targetName='api_transport.exe'),
            Executable('json_converter_module.py', targetName='json_converter.exe'),
            Executable('to_zip_media.py.py', targetName='to_zip_media.exe'),
            Executable('main_console_module.py', targetName='interface_console.exe'),
            Executable('main_module.pyw', targetName='interface.exe')
               ]

excludes = []
#['asyncio','concurrent','ctypes','distutils','lib2to3','multiprocessing','pydoc_data','test','tkinter','unittest','xml','xmlrpc']

zip_include_packages = ['html'
                        'bs4',
                        'lxml',
                        'soupsieve',
                        'select',
                        'unicodedata',
                        'certifi',
                        'chardet',
                        'collections',
                        'email',
                        'encodings',
                        'http',
                        'idna',
                        'importlib',
                        'json',
                        'logging',
                        'requests',
                        'urllib',
                        'urllib3']

includes = ["queue",
            "os",
            "requests",
            "http.client",
            "json",
            "dynaconf",
            "encodings",
            "logger"]

packages = ["os", "requests","http.client","json","dynaconf","logger"]

#        ,'excludes': excludes
#        ,'zip_include_packages': zip_include_packages
options = {
    'build_exe': {
        'include_msvcr': True,
        'includes': includes,
        'packages': packages,
	    'build_exe': build_exe,
        'optimize':1
	}
}

setup(name='API Interface', version='1.0', description='API Interface', executables=executables, options=options)
