import http.client
import ssl
from typing import Pattern

import requests
import json
import os
from shutil import move

import urllib3

import log
import datetime

from config.config import settings
from main_module import init
from json_module import JsonFile
import re


class Api:
    """API Class"""

    # __slots__ = (
    #     'conn', 'headers', 'supplier_data', 'request_plan_data', 'login', 'password', 'supplierId', 'outbox_path',
    #     'current_token', 'protocol', 'server', 'login', 'logger'
    # )

    def __init__(self, api_logger):

        self.logger = api_logger
        self.request_plan_data = JsonFile(settings.REQUEST_PLAN).get_json_data

        self.protocol = settings.PROTOCOL
        self.catalog = settings.CATALOG
        self.server = settings.SERVER
        self.ssl_verify = settings.SSL_VERIFY == 'YES'
        self.conn = http.client.HTTPSConnection(self.server,
                                                context=(ssl._create_unverified_context() if not self.ssl_verify else None))

        self.login = settings.LOGIN
        self.password = settings.PASSWORD
        self.supplierId = settings.SUPPLIERID
        self.outbox_path = settings.OUTBOX_DATA_FOLDER
        self.outbox_arch_path = settings.ARCHIVE_OUTBOX_DATA_FOLDER
        self.inbox_path = settings.INBOX_DATA_FOLDER
        self.inbox_arch_path = settings.ARCHIVE_INBOX_DATA_FOLDER
        self.errors_path = settings.ERRORS_FOLDER
        self.startdate = datetime.datetime.now()

        self.headers = {'accept': 'application/json',
                        'Content-type': 'application/json'}

        res, self.current_token = self.__get_token()
        self.current_token = self.current_token[1:-1] if res else None

        self.headers["Authorization"] = f"Bearer {self.current_token}"

    """Get token request"""

    def __get_token(self):
        r = {'login': self.login, 'password': self.password,
             "supplierId": self.supplierId}
        json_date = json.dumps(r)
        res, result = self.api_request(
            self.request_plan_data["login"]["type"],
            f'{self.catalog}{self.request_plan_data["login"]["method"]}',
            "data", json_date)
        return res, result

    """API request"""

    def api_request(self, type_method, method, successful_execution, json_data='{}', filename=None):

        if filename:
            with open(filename, "r", encoding='utf-8') as read_file:
                try:
                    msg = 'load json object'
                    json_obj = json.load(read_file)
                    msg = 'serealizer json object'
                    json_data = json.dumps(json_obj)
                    msg = 'move file to done folder'
                except Exception as err:
                    err_msg = err.msg
                    err_lineno = err.lineno
                    self.logger.error(
                        f"{msg} - Error of json format: {os.path.join(method_path, request['json_data_path'])} - "
                        f"{err_msg} line-#{err_lineno})")
            # Перемещаем только файлы для отравления
            self.move_to_archive(filename)
        else:
            json_obj = json.loads(json_data)

        if json_data is None:
            return

        error_total = 0
        objects_total = len(json_obj['data']) if 'data' in json_obj else 0
        method = method.replace('$supplierId$', f'{self.supplierId}')
        try:
            self.conn.request(type_method, method, json_data,
                              headers=self.headers)
            res = self.conn.getresponse()
            text_result = res.read().decode('utf-8')
        except Exception as err:
            self.logger.error(f'{method}: {err}')
            return

        result = True if (successful_execution == text_result or successful_execution ==
                          "data") and res.status == 200 else False

        errors = ''

        def msg():
            static = f'({objects_total if objects_total>0 else "0"}' + \
                f',{objects_total-error_total if (objects_total-error_total)>0 else "0"}' + \
                f',{error_total if error_total>0 else "0"})'

            return f'{static}{" "*(20-len(static))} - {type_method} {method.replace(self.catalog, "")} {str(res.status)}: {res.reason} {errors}  '

        if not result:
            dict_result = []
            try:
                # Попытка преоборазовать в JSON-структуру
                dict_result = json.loads(text_result)
            except:
                # Пребразую текст в подобную json структуру
                errors = [text_result]

            errors = self.save_to_file(dict_result, method)
            error_total = len(dict_result)
            text_result = ''
            self.logger.info(msg())
        else:
            self.logger.info(msg())

        return result, text_result

    """Grouping errors before save error to file"""
    @staticmethod
    def get_grouping_error_dict(error, data):

        result = data

        if isinstance(error, str):
            return [error]

        if 'failed' in error:
            error = [_error for elem in error['failed']
                     for _error in error['failed'][elem]]

        # Перебор всех элементов
        for elem in error:
            if 'result' in elem:
                error_type = str(elem['result'])
                del elem['result']
            elif 'messages' in elem:
                error_type = str(elem['messages'])
                del elem['messages']
            else:
                continue
            # Заменяем в описании ошибки значение атрибутов наименование атрибута для унификации ошибок

            for key in elem:
                if elem[key] != '' and not isinstance(elem[key], list) and not isinstance(elem[key], tuple):
                    pattern = rf'\b{str(elem[key])}\b|\b:{str(elem[key])}\b|\b-{str(elem[key])}\b|\s{str(elem[key])}\s'
                    try:
                        error_type = re.sub(
                            pattern, f'[{key}]', error_type, count=1)
                    except Exception as err:
                        print(err)
                    #error_type = error_type.replace(f': {str(elem[key])} ', f': [{key}] ').replace(f'- {str(elem[key])} ', f'- [{key}] ').replace(f' -{str(elem[key])} ', f' -[{key}] ').replace(f' {str(elem[key])} ', f' [{key}] ')

            if error_type in result:
                # Добавляем в сушествующий тип новый элемен
                result[error_type]['list'].append(elem)
                result[error_type]['count'] += 1
            else:
                # Если раньше этого типа не было, то создаём новый тип со значение списка из одного элемента
                result[error_type] = {}
                result[error_type]['count'] = 1
                result[error_type]['list'] = [elem]

        return result

    """Save group error to file"""

    def save_to_file(self, error, method):

        # Get filename
        file_error = method.split(
            '/')[-1] if method.split('/')[-1][0] != '?' else method.split('/')[-2]
        file_error = f'{file_error}{self.startdate.strftime(settings.POSTFIX_DATE_FORMAT)}.json'

        # Reading this file to dict if file is existing
        if os.path.isfile(os.path.join(self.errors_path, file_error)):
            with open(os.path.join(self.errors_path, file_error), mode='r', encoding='utf8') as f:
                old_data = json.load(f)
        else:
            old_data = {}

        data = self.get_grouping_error_dict(error, old_data)
        with open(os.path.join(self.errors_path, file_error), mode='w', encoding='utf8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        errors_list = [elem for elem in data]
        return errors_list

    """API Send file"""

    def send_file_response(self, type_method, method, successful_execution, media_path):

        method = method.replace('$supplierId$', f'{self.supplierId}')
        _method = f'{self.protocol}://{self.server}{method}'
        payload = {}
        files = [('uploadedFile', open(media_path, 'rb'))]
        headers = {'Authorization': f'Bearer {self.current_token}'}

        try:
            if not self.ssl_verify:
                urllib3.disable_warnings()
            res = requests.request(type_method, _method,
                                   headers=headers, data=payload, files=files, verify=self.ssl_verify)
            text_result = res.content.decode('utf-8')
        except Exception as err:
            self.logger.error(f'{method}: {err}')
            return False

        result = True if '{"failed":{}}' == text_result or successful_execution == "date" \
                         and res.status_code == 200 else False

        msg = f'файл               - {type_method} {method.replace(self.catalog, "")} {str(res.status_code)}: {res.reason} {media_path}'
        if not result:
            error = json.loads(
                text_result) if res.status_code == 200 else text_result
            errors = self.save_to_file(error, method) if res.status_code == 200 else [
                text_result]
            msg = f'{msg} - {errors}'
            text_result = ""
        self.logger.info(msg)

        return result, text_result

    @staticmethod
    def get_file_list(filename, path, ext, postfix=settings.POSTFIX_FILENAME_SEPARATOR):
        # get filename without extension
        file_name = (filename.split('.'))[0] + postfix
        files_list = [os.path.join(path, f) for f in os.listdir(path)
                      if (len(postfix) > 0 and f[0:len(file_name)] == file_name
                          or len(postfix) == 0 and f == filename
                          or 'uploadProductsImages' in filename and 'uploadProductsImages' in f
                          )
                      and f.endswith(f'.{ext}')]
        return files_list

    def move_to_archive(self, src):

        if settings.FILES_MOVE_TO_ARCHIVE == "YES":
            # Перемещаем только файлы для отравления
            filename, ext = os.path.basename(src).split('.')
            filename = f'{filename}{datetime.datetime.now().strftime(settings.POSTFIX_DATE_FORMAT)}.{ext}'
            destination = os.path.join(
                self.outbox_arch_path, os.path.basename(filename))
            move(src, destination)

        return

    def run_requests(self, request):

        if self.current_token is None:
            return

        method_path = self.outbox_path if request["type"] == "POST" else self.inbox_path

        if "media_path" in request:
            zip_list = self.get_file_list(
                filename=request["media_path"], path=method_path, ext='zip')
            if len(zip_list) == 0:
                self.logger.warning(
                    f'файл                 - {request["type"]} {request["method"]} - не найден файл')
            for _file_name in zip_list:
                self.send_file_response(request["type"], f'{self.catalog}{request["method"]}',
                                        request["successful_execution"], _file_name)
                self.move_to_archive(_file_name)

        elif request["type"] == "POST" and "json_data_path" in request:
            json_list = self.get_file_list(
                filename=request["json_data_path"], path=method_path, ext='json')
            if len(json_list) == 0:
                self.logger.warning(
                    f'(0,0,0)              - {request["type"]} {request["method"]} - не найден файл')

            for _file_name in json_list:
                self.api_request(
                    type_method=request["type"], method=f'{self.catalog}{request["method"]}',
                    successful_execution=request["successful_execution"], filename=_file_name)
        elif request["type"] == "GET" and "json_data_path" in request:
            res, result = False, []
            with open(os.path.join(os.getcwd(), method_path, request["json_data_path"]), "w", encoding='utf-8') as file:
                try:
                    res, result = self.api_request(
                        request["type"], f'{self.catalog}{request["method"]}', request["successful_execution"])
                    if res:
                        file.write(result)
                    else:
                        self.logger.error(f'{request["method"]} : {result}')
                except Exception as err:
                    self.logger.error(f'{request["method"]} : {err}')

            return res, result

    def run_requests_all(self):
        """Run everything requests api from plan"""
        for request in self.request_plan_data["plan"]:
            self.run_requests(request)


def run(logger_arg):

    Api(logger_arg).run_requests_all()


if __name__ == "__main__":
    # Init interface folder
    init()
    # Init logger
    logger = log.init()

    logger.info(f'(общ,загр,ошибок)      НАЧАЛО:ТРАНСПОРТ API')
    run(logger)
    logger.info(f'(общ,загр,ошибок)      КОНЕЦ:ТРАНСПОРТ API')
