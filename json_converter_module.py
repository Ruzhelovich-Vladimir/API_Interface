"""
 Модуль конвертации данных из таблицы для json

 Может передаваться список файлов, начало файла соотвествует типу json файла

"""

from os import path, listdir
import sys
import json
import csv
from config.config import settings
import log
from main_module import init

class ConvertFilesToJson:

    def __init__(self, list_files=[], logger=None):

        self.logger = logger if logger else log.init()

        for file_name in list_files:

            if settings.DEPENDENT_FILENAME_SEPARATOR in file_name:
                continue
            schema = self.get_schema(file_name)
            if not schema:
                continue
            data_ = self.get_list_data_from_text_file(file_name)
            if not data_list or len(data_list) == 0:
                continue

        ## TODO преобразование файлов


    def get_dict(self, file_name):

        ## TODO Получение словаря из текстового файла (рекурсия)

        """Get dict object from text file

                Args:
                    file_name ([type]): file name
                    dependent_dict ([dict]): dependent objects
                Returns:
                    [dict]: dict object
        """
        result = {}
        # Получаем схему конвертации
        schema = self.get_schema(file_name)
        if not schema:
            logger.warning(f'Не найдена схемы конвертации для файла {file_name}')
            return {}

        # Получаем шапку текстового файла
        header_list = self.get_dict_header_from_text_file(file_name)
        if not header_list:
            logger.warning(f'Файл {file_name} пустой')
            return {}

        # Получаем табличную часть файла
        data_list = self.get_list_data_from_text_file(file_name)
        if not data_list or len(data_list) == 0:
            logger.warning(f'Файл {file_name} не содержит данных')
            return {}

        return result

    @staticmethod
    def get_schema(file_name):
        """Get json file schema

        Args:
            file_name ([type]): file name

        Returns:
            [dict]: description json schema
        """

        result = ''
        schema_file_name = path.basename(file_name)
        schema_file_name = schema_file_name[:schema_file_name.find(
            settings.POSTFIX_FILENAME_SEPARATOR)-len(schema_file_name)]
        schema_file_name = path.join(
            settings.SCHEMES_JSON_DATA_FOLDER, f'{schema_file_name}.json')
        with open(schema_file_name, 'r', encoding='utf8') as f:
            result = json.load(f)

        return result

    @staticmethod
    def get_dict_header_from_text_file(file_name):
        """Get header dict from text file

        Args:
            file_name ([string]): file name

        Returns:
            [dict]: {'field_name'[string]:index[int]}
        """

        with open(file_name, 'r', encoding='utf8') as f:
            data = f.readline()

        return {name: inx for inx, name in
                enumerate(data.split(settings.COL_SEPARATOR_TABLE))} if len(data) > 1 else None

    @staticmethod
    def get_list_data_from_text_file(file_name):
        """Get list data from text file

        Args:
            file_name ([type]): file name

        Returns:
            [list]: data list [row][colm]
        """

        result = ''
        with open(file_name, 'r', encoding='utf8') as f:
            result = f.read()

        header = result.split('\n')[0].split(settings.COL_SEPARATOR_TABLE)
        result = [{header[col]:value for col, value in enumerate(row.split(settings.COL_SEPARATOR_TABLE))}
                  for row in result.split('\n')[1:]] if result else None

        pass

        return result


def run(argv, logger_arg):
    """Transform txt file to json
            Args:
                argv: file list or null
                logger_arg: logger object

            Returns:
                json file
    """

    logger = logger_arg

    if len(argv) > 1:
        file_list = argv[1:]  # Если передаётся список
    else:
        # Обрабатываем все файлы в каталоге
        file_list = [filename for filename in listdir(
            settings.OUTBOX_DATA_FOLDER) if '.txt' == filename[-4:]]

    # Добавляем пусть к каталогу
    file_list = [path.join(settings.OUTBOX_DATA_FOLDER, file) for file in file_list]
    ConvertFilesToJson(file_list)


if __name__ == "__main__":
    init()
    logger = log.init()
    logger.info(f'НАЧАЛО:КОНВЕРТАЦИЯ ДАННЫХ API')
    run(sys.argv, logger)
    logger.info(f'КОНЕЦ:КОНВЕРТАЦИЯ ДАННЫХ API')


    # def get_dependent_dict(self, list_files):
    #     ## TODO получение словаря зависимости
    #
    #     # dependent_dict = { main_table: { dependent_table : { foreing_key : { data_dict }, ...}, ...}, }
    #
    #     result = {}
    #     for file_name in list_files:
    #         if settings.DEPENDENT_FILENAME_SEPARATOR not in file_name:
    #             continue
    #         if len(settings.POSTFIX_FILENAME_SEPARATOR) > 0:
    #             key = f'{os.path.basename(file_name).split(settings.DEPENDENT_FILENAME_SEPARATOR, maxsplit=1)[0]}' \
    #                   f'{settings.POSTFIX_FILENAME_SEPARATOR}' \
    #                   f'{os.path.basename(file_name).split(settings.POSTFIX_FILENAME_SEPARATOR,maxsplit=1)[1]}'
    #             table_name = f'{os.path.basename(file_name).split(settings.DEPENDENT_FILENAME_SEPARATOR, maxsplit=1)[1]}'
    #             table_name = table_name.split(settings.POSTFIX_FILENAME_SEPARATOR, maxsplit=1)[0]
    #             data_dict = self.get_dict(file_name)
    #             if key in result and isinstance(result[key], dict):
    #                 result[key][table_name] = data_dict
    #             else:
    #                 result[key] = {table_name: data_dict}
    #     return result
