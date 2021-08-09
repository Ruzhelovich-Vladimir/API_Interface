rem .\venv\Scripts\Activate && pyinstaller -n api_module.exe -F -w api_module.py && pyinstaller -n api_module_debug.exe -F api_module.py && pyinstaller -n interface.exe -F -w main_module.py && pyinstaller -n interface_debug.exe -F main_module.py
.\venv\Scripts\Activate && pyinstaller -n api_module_debug.exe -F api_module.py && pyinstaller -n to_zip_media_debug.exe -F  to_zip_media.py 
