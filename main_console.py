import log
import sys,os
import json_converter, api_transport, to_zip_media
import log

from config.config import settings


def init_interface_folders():
    
    dir_ls = (settings.SCHEMES_JSON_DATA_FOLDER,settings.ARCHIVES_FOLDER,settings.CONF_FILENAME,settings.OUTBOX_DATA_FOLDER,
                settings.INBOX_DATA_FOLDER,settings.ARCHIVE_OUTBOX_DATA_FOLDER,settings.ARCHIVE_INBOX_DATA_FOLDER,settings.ERRORS_FOLDER)
    
    for path in dir_ls:
        try:
            os.makedirs(path)
        except:
            pass
        else:
            logger.info(f'Каталог создан: {path}')

    
def run():

    init_interface_folders()
    
    logger = log.init()
    logger.info(f'НАЧАЛО:КОНВЕРТАЦИЯ ДАННЫХ API')
    json_converter.run(sys.argv,logger)
    logger.info(f'КОНЕЦ:КОНВЕРТАЦИЯ ДАННЫХ API')
    
    logger.info(f'НАЧАЛО:АРХИВАЦИЯ КАРТИНОК API')
    to_zip_media.run(logger)
    logger.info(f'КОНЕЦ:АРХИВАЦИЯ КАРТИНОК API')
    
    logger.info(f'НАЧАЛО:ТРАНСПОРТИРОВКА ПАКЕТОВ API')
    api_transport.run(logger)
    logger.info(f'КОНЕЦ:ТРАНСПОРТИРОВКА ПАКЕТОВ API')



if __name__ == "__main__":

    run()

