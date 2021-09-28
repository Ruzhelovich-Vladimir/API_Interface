from config.config import settings

import os
import zipfile
import log

from main_module import init

PATH = settings.OUTBOX_DATA_FOLDER
MEDIA_TYPES = settings.MEDIA_TYPES
SEPARATOR = '_'

def run(logger):

    init()
    default_path = os.path.abspath(os.curdir)
    os.chdir(PATH)
    files = os.listdir()

    for file in files:
        for ext in MEDIA_TYPES:
            if file.endswith(f'.{ext}'):
                file_path=os.path.join(file)
                arch_name = os.path.join(f'uploadProductsImages_{file[:-4].split(SEPARATOR)[0]}.zip')
                with zipfile.ZipFile(arch_name, mode='a', compression=zipfile.ZIP_DEFLATED) as zf:
                    zf.write(file_path)
                os.remove(file_path)
                logger.info(f'Добавлен в архив файл: {file}')
    
    os.chdir(default_path)

if __name__ == '__main__':
    logger = log.init()
    logger.info(f'                       НАЧАЛО:АРХИВАЦИЯ КАРТИНОК API')
    run(logger)
    logger.info(f'                       КОНЕЦ:АРХИВАЦИЯ КАРТИНОК API')