import sys
import json_converter_module
import api_module
import to_zip_media
import log
from main_module import init


def run():
    init()
    logger = log.init()
    logger.info(f'НАЧАЛО:КОНВЕРТАЦИЯ ДАННЫХ API')
    json_converter_module.run(sys.argv, logger)
    logger.info(f'КОНЕЦ:КОНВЕРТАЦИЯ ДАННЫХ API')

    logger.info(f'НАЧАЛО:АРХИВАЦИЯ КАРТИНОК API')
    to_zip_media.run(logger)
    logger.info(f'КОНЕЦ:АРХИВАЦИЯ КАРТИНОК API')

    logger.info(f'НАЧАЛО:ТРАНСПОРТИРОВКА ПАКЕТОВ API')
    api_module.run(logger)
    logger.info(f'КОНЕЦ:ТРАНСПОРТИРОВКА ПАКЕТОВ API')


if __name__ == "__main__":
    run()
