'''
 Модуль конвертации данных из таблицы для json

 Может передаваться список файлов, начало файла соотвествует типу json файла

'''

from json import encoder
from os import path, listdir
import sys
import json
from shutil import move

from config.config import settings
import log

logger = None

class convert_files_to_json:

    def __init__(self, list_files):

        for file_name in list_files:

            schema = self.get_schema(file_name)
            if not schema:
                continue
            header_list = self.get_dict_header_from_text_file(file_name)
            if not header_list:
                continue
            data_list = self.get_list_data_from_text_file(file_name)
            if not data_list or len(data_list) == 0:
                continue

            json_data = self.get_json(schema=schema, header_list=header_list,
                                      data_list=data_list)
            json_file_name = path.join(f'{file_name[:-4]}.json')

            with open(json_file_name, 'w', encoding='utf8') as f:
                f.write(json_data)

            dst_file_name = path.join(
                settings.ARCHIVES_FOLDER, path.basename(file_name))
            move(file_name, dst_file_name)

    @staticmethod
    def get_json(schema, header_list, data_list):

        result = {}
        result['data'] = []
        data_elem = {}

        for row in data_list:
            for name_field, field_def in schema.items():
                # Получение значение в талицы по наименованию поля схеме, если нет по смотрим по умолчению
                value = None
                if field_def['type'] == 'list':
                    value = []
                elif name_field in header_list:
                    value = row[header_list[name_field]]
                elif 'default' in field_def:
                    value = field_def['default']

                if not value:
                    continue

                if "data:" in field_def['key']:
                    keys = field_def['key'].split(':')
                    data_key = keys[1]
                    data_elem[data_key] = value
                else:
                    if field_def['key'] not in result:
                        result[field_def['key']] = value

            result['data'].append(data_elem)
        json_data = json.dumps(result)

        return json_data

    @staticmethod
    def get_dict_header_from_text_file(file_name):
        """Get header dict from text file

        Args:
            file_name ([string]): file name

        Returns:
            [dict]: {'field_name'[string]:index[int]}
        """

        data = None
        with open(file_name, 'r', encoding='utf8') as f:
            data = f.readline()

        return {name: inx for inx, name in enumerate(data.split(settings.COL_SEPARATOR_TABLE))} if len(data) > 1 else None

    @staticmethod
    def get_schema(file_name):
        """Get json file schema

        Args:
            file_name ([type]): file name

        Returns:
            [dict]: description json schema
        """

        result = None
        schema_file_name = path.basename(file_name)
        schema_file_name = schema_file_name[:schema_file_name.find(
            settings.POSTFIX_FILENAME_SEPARATOR)-len(schema_file_name)]
        schema_file_name = path.join(
            settings.SCHEMES_JSON_DATA_FOLDER, f'{schema_file_name}.json')
        with open(schema_file_name, 'r', encoding='utf8') as f:
            result = json.load(f)

        return result

    @staticmethod
    def get_list_data_from_text_file(file_name):
        """Get list data from text file

        Args:
            file_name ([type]): file name

        Returns:
            [list]: data list [row][colm]
        """

        result = None
        with open(file_name, 'r', encoding='utf8') as f:
            result = f.read()
        result = [row.split(settings.COL_SEPARATOR_TABLE)
                  for row in result.split('\n')[1:]] if result else None

        return result


def run(argv,logger_arg):

    logger=logger_arg

    if len(argv) > 1:
        FILE_LIST = argv[1:]  # Если передаётся список
    else:
        # Обрабатываем все файлы в каталоге
        FILE_LIST = [filename for filename in listdir(
            settings.OUTBOX_DATA_FOLDER) if '.txt' == filename[-4:]]

    # Добавляем пусть к каталогу
    FILE_LIST = [path.join(settings.OUTBOX_DATA_FOLDER, file) for file in FILE_LIST]
    convert_files_to_json(FILE_LIST)


if __name__ == "__main__":

    logger = log.init()
    logger.info(f'НАЧАЛО:КОНВЕРТАЦИЯ ДАННЫХ API')
    run(sys.argv,logger)
    logger.info(f'КОНЕЦ:КОНВЕРТАЦИЯ ДАННЫХ API')
