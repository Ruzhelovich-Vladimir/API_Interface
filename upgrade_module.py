# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:         upgrade_module.py
# Purpose:      Модуль обновления интерфейса через SVN-канал компании САН Инбев
#
# Author:       Ruzhelovich Vladimir
#
# Created:      07.07.2021
# Copyright:    (c) Ruzhelovich Vladimir
# E-Mail:       Ruzhelovich.Vladimir@gmail.com
# Licence:      freeware for partners of Inbev
#-------------------------------------------------------------------------------

import pysvn
import os
import shutil
import codecs

# init settings
from config.config import settings
# init interface folders
from main_module import init
import log


ChangeType={
    pysvn.wc_status_kind.none: u'does not exist (не существует)', \
    pysvn.wc_status_kind.unversioned: u'is not a versioned thing in this wc (не версионный)',
    pysvn.wc_status_kind.normal: u'не изменен', \
    pysvn.wc_status_kind.added: u'добавлен', \
    pysvn.wc_status_kind.missing: u'under v.c., but is missing', \
    pysvn.wc_status_kind.deleted: u'удалён файл', \
    pysvn.wc_status_kind.replaced: u'заменён', \
    pysvn.wc_status_kind.modified: u'модифицирован', \
    pysvn.wc_status_kind.merged: u'local mods received repos mods (мегрирован)', \
    pysvn.wc_status_kind.conflicted: u'local mods received conflicting repos mods (конфликт)', \
    pysvn.wc_status_kind.ignored: u'a resource marked as ignored (игнорируется)', \
    pysvn.wc_status_kind.obstructed: u'an unversioned resource is in the way of the versioned resource', \
    pysvn.wc_status_kind.external: u'an unversioned path populated by an svn:external property', \
    pysvn.wc_status_kind.incomplete: u'a directory doesnt contain a complete entries list' \
            }

class SVN:

    def __init__(self, logger_arg):

        self.logger = logger_arg
        self.server_svn_path = os.path.join(settings.SVN_PROTOCOL, settings.SVN_HOST, settings.SVN_PATH)
        self.wc_path = settings.SVN_WORK_COPY_PATH
        self.login = settings.SVN_LOGIN
        self.password = settings.SVN_PASSW

        self.wc_svn_system_path = os.path.join(self.wc_path, u'.svn')
        self.temp_path = os.path.join(self.wc_path, 'tmp_wc')

        self.client=self.connect()


    '''
            Обработчик проверки доверительных соединений 
    '''
    @staticmethod
    def callback_ssl_server_trust_prompt(trust_data):
        return True, trust_data['failures'], True

    def get_client(self):
        try:
            txt_command = u'Авторизация к локальной рабочей копии SVN'
            client = pysvn.Client()
            client.set_default_username(self.login)
            client.set_default_password(self.password)
            client.callback_ssl_server_trust_prompt = self.callback_ssl_server_trust_prompt
        except Exception as error:
            self.logger.error(f'{txt_command} : {error}')
            return None
        return client

    ###############################################################
    def is_repository(self):
        ###########################################################
        # Определяет является ли каталог рабочим локальным репозторием
        ###########################################################

        if not self.connect:
            return False
        try:
            if self.connect():
                txt_command = u'Получение информации о локальной рабочей копии SVN'
                self.client.info(self.server_svn_path)
        except Exception as error:
            self.logger.error(f'{txt_command} : {error}')
            return False

        return True

    ###############################################################
    def is_url_changed(self):
        ###########################################################
        # Возвращаети True если URL рабочей коппии не соответствует
        # URL в настройках
        ###########################################################
        try:
            txt_command = u'Получение информации о локальной рабочей копии SVN'
            entry = self.client.info(self.wc_path)
        except Exception as error:
            self.logger.error(f'{txt_command} : {error}')
        else:
            # URL адрес рабочий копии
            url_work_copy = entry.url
            # Если адрес заканчивается на '/', то данный символ вырезаем
            if url_work_copy[-1:] == '/':
                url_work_copy = url_work_copy[:len(url_work_copy) - 1]
            # URL репозитория
            url_server = self.server_svn_path
            # Если адрес заканчивается на '/', то данный символ вырезаем
            if url_server[-1:] == '/':
                url_server = url_server[:len(url_server) - 1]
            return url_server != url_work_copy

        return False

    def run(self):
        ##########################################################
        #   Обновление интерфейса
        #   Алгоритм:
        #       1. Создаем репозиторий, если каталог не является рабочей копии
        #       2. Если URL изменился, то делаем его обычным каталогом, и создаём репозиторий
        #       3. Обновляем рабочую копию
        #       4. Рещаем конфликты
        #       5. Обвновляем интерфейс
        #       6. Отправляем изменения
        #       7. Предоставляем права всем пользователям
        ##########################################################

        # Шаг 1
        if not self.is_repository() or self.is_url_changed():
            txt_command = u'Создание рабочей копии...' if not self.is_repository() else \
                txt_command = u'Изменение адреса URL рабочий копии...'
            self.checkout()
        # Шаг 3
        txt_command = u'Обновляем рабочую копию'
        UpdateFlag = self.update()
        # Шаг 4
        txt_command = u'Рещаем конфликты'
        ConflictRepository()
        # Шаг 5
        txt_command = u'Обвновляем интерфейс'
        UpgradeRelease()  # Если пришёл модуль обновления модуля обмена, то запускаем процесс обновления модуля
        # Шаг 6
        txt_command = u'Отправляем изменения'
        CommitRepository()
        # Шаг 7
        GrandFolders()
        log.InLog(CustID, u'Окончание обновления', True, '', True, False)

    def checkout(self):
        ###########################################################
        # Создать рабочую копию
        ###########################################################

        try:
            if not os.path.isdir(pathTemp):
                txt_command = u'Создаём временный каталог для репозитория:' + pathTemp
                os.mkdir(pathTemp)
            if os.path.isdir(svnpathTemp):
                txt_command = u'Удаляем временный каталог .svn:' + svnpathTemp
                GrandFolders(svnpathTemp)
                moveFolder(svnpathTemp)
            if os.path.isdir(svnpathClient):
                txt_command = u'Удаляем каталог .svn:' + pathTemp
                GrandFolders(svnpathClient)
                RemoveFolder(svnpathClient)

            txt_command = u'Авторизация репозитория SVN'
            client = pysvn.Client()
            client.set_default_username(xdata['User'])
            client.set_default_password(xdata['Password'])
            client.callback_ssl_server_trust_prompt = callback_ssl_server_trust_prompt
            txt_command = u'Создание рабочей копии в ' + pathTemp
            client.checkout(pathServer, pathTemp, ignore_externals=True)
            txt_command = u'Предоставление прав к каталогу ' + svnpathTemp
            client = []
            GrandFolders(xdata, svnpathTemp)
            txt_command = u'Перенос каталога ' + svnpathTemp + u" в " + svnpathClient
            shutil.move(svnpathTemp, svnpathClient)

            txt_command = u'Авторизация репозитория SVN'
            client = pysvn.Client()
            client.set_default_username(xdata['User'])
            client.set_default_password(xdata['Password'])
            client.callback_ssl_server_trust_prompt = callback_ssl_server_trust_prompt
            txt_command = u'Обновляем репозиторий, восстанавливая отсутствующие файлы'
            client.update(pathClient, recurse=True)
            txt_command = u'Удаляем каталог: ' + pathTemp
            RemoveFolder(xdata, pathTemp)
            txt_command = u'Создание рабочей копии в ' + pathClient
        except Exception as e:
            log.InLog(CustID, txt_command, False, str(e), True)
        else:
            log.InLog(CustID, txt_command, True, u'', False)

###########################################################
def Copy_Object_SVN(xdata,src, dst):
    ###########################################################
    # Архивирование файлов, которые находятся в локальной папке, существующие в репозитории 
    ###########################################################

    pathServer = xdata['ServerPath']
    txt_command = u'Архивирование объектов из локального каталога, которые находятся в SVN'

    CustID=xdata['Warehouse']

    Result=False
   
    try:
        txt_command = u'Авторизация репозитория SVN'
        client = pysvn.Client()
        client.set_default_username(xdata['User'])
        client.set_default_password(xdata['Password'])
        client.callback_ssl_server_trust_prompt = callback_ssl_server_trust_prompt
        txt_command = u'Получаем список объектов в репозитории :'+pathServer
        objects_svn=client.ls(pathServer)
    except Exception as e:
           log.InLog(CustID, txt_command, False, str(e),True)
           Result=False
    else:
        Result=True
        for _object_ in objects_svn:
            object_svn=os.path.join(_object_.name.replace(pathServer,u'')) #Получаем объкт SVN (имя файла) 
            #Получаем пусть к файлу источника и приёмника и svn   
            srcname = os.path.join(src, object_svn)
            dstname = os.path.join(dst, object_svn)
            if os.path.isfile(srcname) and str(_object_['kind'])==u'file' :
                #Если объект SVN являетя файлом и он существует в рабочей копии             
                try:
                    txt_command = u'Копирование файла:'+srcname+u' в '+dstname
                    log.InLog(CustID, txt_command, True, '',False)
                    shutil.copy(srcname, dstname)
                    
                    txt_command = u'Удаляем файл:'+srcname
                    log.InLog(CustID, txt_command, True, '',False)
                    os.remove(srcname)
                except Exception as e:
                    log.InLog(CustID, txt_command, False, str(e),True)
                    Result=False
            elif os.path.isdir(srcname) and str(_object_['kind'])==u'dir':
                #Если объект является каталогом и он существует, то копируем весь каталог
                Result=MoveFolder(xdata,srcname, dstname)
                try:
                    if os.listdir(srcname)== []:
                        txt_command = u'Удаление пустого каталога '+srcname
                        os.rmdir(srcname)
                        log.InLog(CustID, txt_command, True, '',False)
                except Exception as e:
                    log.InLog(CustID, txt_command, False, str(e),True)
                    Result=False    
    return Result

###############################################################
def MoveFolder(xdata,src, dst,Result=True):
    ###########################################################
    # Копирование каталога рекурсивно
    ###########################################################

    CustID=xdata['Warehouse']

    res=Result #Переменная, статуса выполнения рекурсии

    # Если каталог приёмник существует и статус = True
    if not os.path.isdir(dst) and res==True:
        try:
            txt_command = u'Создаём каталог '+dst
            os.makedirs(dst)
            log.InLog(CustID, txt_command, True,u'',False)
        except Exception as e:
            log.InLog(CustID, txt_command, False, str(e),True)
            res=False

    if res==True and os.path.isdir(src):
        for object in os.listdir(src):
            src_1=os.path.join(src,object)
            dst_2=os.path.join(dst,object)
            if os.path.isdir(src_1):

                txt_command = u'Копирование каталога '+src_1+u'->'+dst_2
                res=MoveFolder(xdata,src_1, dst_2,res)
                log.InLog(CustID, txt_command, True,u'',False)
                if os.listdir(src_1)== []:
                    txt_command = u'Удаление пустого каталога '+src_1
                    os.rmdir(src_1)
                    log.InLog(CustID, txt_command, True,u'',False)
            elif os.path.isfile(src_1):
                try:
                    txt_command = u'Копирование файла '+src_1+u'->'+dst_2
                    shutil.copy(src_1,dst_2)
                    log.InLog(CustID, txt_command, True,u'',False)

                    txt_command = u'Удаляем скопированный файл:'+src_1
                    os.remove(src_1)
                    log.InLog(CustID, txt_command, True,u'',False)
                except Exception as e:
                    log.InLog(CustID, txt_command, False, str(e),True)
                    res=False
    return res

###############################################################
def CreateRepository(xdata):
    ###########################################################
    # Создать репозиторий
    ########################################################### 

    pathClient = xdata['LocalRepository']
    svnpathClient = os.path.join(pathClient,u'.svn')

    pathTemp = os.path.join(pathClient,TempSVN)
    svnpathTemp = os.path.join(pathTemp,'.svn')
    
    pathServer = xdata['ServerPath']
    CustID=xdata['Warehouse']
    
    try:       
        if not os.path.isdir(pathTemp):
            txt_command = u'Создаём временный каталог для репозитория:'+pathTemp
            os.mkdir(pathTemp)
        if os.path.isdir(svnpathTemp):
            txt_command = u'Удаляем временный каталог .svn:'+svnpathTemp
            GrandFolders(xdata,svnpathTemp)
            moveFolder(xdata,svnpathTemp)
        if os.path.isdir(svnpathClient):
            txt_command = u'Удаляем каталог .svn:'+pathTemp
            GrandFolders(xdata,svnpathClient)
            RemoveFolder(xdata,svnpathClient)
            
        txt_command = u'Авторизация репозитория SVN'
        client = pysvn.Client()
        client.set_default_username(xdata['User'])
        client.set_default_password(xdata['Password'])
        client.callback_ssl_server_trust_prompt = callback_ssl_server_trust_prompt
        txt_command = u'Создание рабочей копии в '+pathTemp
        client.checkout(pathServer,pathTemp,ignore_externals=True)
        txt_command = u'Предоставление прав к каталогу '+svnpathTemp
        client=[]
        GrandFolders(xdata,svnpathTemp)
        txt_command = u'Перенос каталога '+svnpathTemp+u" в "+ svnpathClient
        shutil.move(svnpathTemp, svnpathClient)
        
        txt_command = u'Авторизация репозитория SVN'
        client = pysvn.Client()
        client.set_default_username(xdata['User'])
        client.set_default_password(xdata['Password'])
        client.callback_ssl_server_trust_prompt = callback_ssl_server_trust_prompt
        txt_command = u'Обновляем репозиторий, восстанавливая отсутствующие файлы'
        client.update(pathClient,recurse=True)
        txt_command = u'Удаляем каталог: '+pathTemp
        RemoveFolder(xdata,pathTemp)
        txt_command = u'Создание рабочей копии в '+pathClient
    except Exception as e:
        log.InLog(CustID, txt_command, False, str(e),True)
    else:
        log.InLog(CustID, txt_command, True, u'',False)

###############################################################        
def UpdateRepository(xdata):
    ###########################################################
    # Обновить репозиторий
    ###########################################################
    pathClient = xdata['LocalRepository']
    pathServer = xdata['ServerPath']

    UpdateFlagWC = os.path.join(pathClient, UpdateFolder, update_flag) #Флаг обновления
    UpdateInterfaceFlag=os.path.join(pathClient, update_interface_flag)

    CustID=xdata['Warehouse']
    Flag=False
    
    try:
        txt_command = u'Авторизация репозитория SVN'
        client = pysvn.Client()
        client.set_default_username(xdata['User'])
        client.set_default_password(xdata['Password'])
        client.callback_ssl_server_trust_prompt = callback_ssl_server_trust_prompt
        txt_command = u'Получение списка обновлений'

        # Получаем информацию о текущей ревизии
        entry = client.info(pathClient)
        old_rev = entry.revision.number
        # Обновляем репозиторий
        
        txt_command = u'Обновление репозитория'
        revs = client.update(pathClient)
        # Получаем инфомацию о новой ревизии
        new_rev = revs[-1].number

        head = pysvn.Revision(pysvn.opt_revision_kind.number, old_rev)
        end = pysvn.Revision(pysvn.opt_revision_kind.number, new_rev)

        FILE_CHANGE_INFO = {
                pysvn.diff_summarize_kind.normal: ' ',
                pysvn.diff_summarize_kind.modified: u'изменен',
                pysvn.diff_summarize_kind.delete: u'удалён',
                pysvn.diff_summarize_kind.added: u'добавлен',
                }
        summary = client.diff_summarize(pathClient, head, pathClient, end)
        list_change=[]
        list_update=[]

        for info in summary:
            path = info.path
            if os.path.basename(path) not in ('ae.log','version.csv'):  
                file_changed = FILE_CHANGE_INFO[info.summarize_kind]
                if file_changed in (u"изменен",u"добавлен",u'удалён'):
                    txt_command = u'Список изменений на сервере SVN: файл '+path.replace(u'/',u'\\')+u'-'+file_changed
                    if (os.path.basename(path) in inst_filename_list) and os.path.dirname(path)=="Update":
                        if file_changed!=u'удалён':
                            list_update.append(path.replace(u'/',u'\\'))                           
                    else:
                        list_change.append(path.replace(u'/',u'\\')+"-"+file_changed)
                    log.InLog(CustID, txt_command, True, u'',False)

        if list_change!=[]:#Создаём флаг обновления интерфейса со списком изменений
            txt_command = u'Создаём флаг обновления интерфейса:'+UpdateInterfaceFlag
            with codecs.open(UpdateInterfaceFlag,u'a',encoding="cp1251") as txt_file:
                for txtstr in list_change:
                    txt_file.write(txtstr+u'\n')
                txt_file.close()

        if list_update!=[]:
            txt_command = u'Создаём флаг обновления модуля обмена:'+UpdateFlagWC
            with codecs.open(UpdateFlagWC,u'a',encoding="cp1251") as txt_file:
                for txtstr in list_update:
                    txt_file.write(txtstr+u'\n')
                txt_file.close()
            log.InLog(CustID, txt_command, True, u'',False)
            txt_command = u'Найдено обновление модуля обмена, будет запущен процесс автообновления'
           
               
    except Exception as e:
        log.InLog(CustID, txt_command, False, str(e),True)
    else:
        log.InLog(CustID, txt_command, True, u'',False)


###############################################################
def CommitRepository(xdata, mes = True):
    ###########################################################
    # Фиксировать изменения репозитория
    ###########################################################
  
    pathClient = xdata['LocalRepository']
    CustID=xdata['Warehouse']
    try:
        txt_command = u'Авторизация репозитория SVN'
        client = pysvn.Client()
        client.set_default_username(xdata['User'])
        client.set_default_password(xdata['Password'])
        client.callback_ssl_server_trust_prompt = callback_ssl_server_trust_prompt
        txt_command = u'Удаляет все блокировки рабочей копии'
        client.cleanup(pathClient)
        # Прохожу по всем изменениям
        txt_command = u'Отправка локальных изменений'
        for _object_ in client.status(path=pathClient):
            #Флаг объект является запрещённый для изменений
            f_no_commit=(os.path.basename(_object_.path).find(u'.exe')!=-1 \
                   or os.path.basename(_object_.path).find(u'.dll')!=-1 \
                   or os.path.basename(_object_.path).find(u'.zip')!=-1  \
                   or os.path.basename(_object_.path).find(u'.cmd')!=-1  \
                   or os.path.basename(_object_.path).find(u'.bat')!=-1 \
                   or os.path.basename(_object_.path).find(u'.vbs')!=-1)
            if  f_no_commit==False and os.path.basename(_object_.path) not in ('ae.log','version.csv') and \
                   _object_.text_status not in (pysvn.wc_status_kind.normal,pysvn.wc_status_kind.unversioned):
                try:
                    if _object_.text_status not in(pysvn.wc_status_kind.modified,pysvn.wc_status_kind.conflicted):
                        txt_command = u'Отменяю изменение:'+_object_.path+'-'+ChangeType[_object_.text_status]
                        client.revert(_object_.path)
                    elif _object_.text_status == pysvn.wc_status_kind.modified :
                        txt_command = u'Отправляю изменения в :'+_object_.path
                        client.checkin([_object_.path], u'CFD * '+_object_.path+u' * '+VERSION)
                except Exception as e:
                    try:
                        # Решение конфликта каталога ISSUE: #7946
                        # (в репозитории нет каталога, в рабочей копии есть каталог, добавлен как репозиторий)
                            client.resolved([_object_.path])                           #Решаем конфликт
                            client.checkin([_object_.path], u'CFD * '+_object_.path+u' * '+VERSION)
                    except Exception as e:
                        log.InLog(CustID, txt_command, False, str(e),True)
                    else:
                        log.InLog(CustID, txt_command, True, u'',False)
                else:
                    log.InLog(CustID, txt_command, True, u'',False)
            elif ( f_no_commit==True \
                   and _object_.text_status in(pysvn.wc_status_kind.modified,pysvn.wc_status_kind.conflicted)):
                #Если была попытка изменить файл exe, отменяем изменение
                try:
                    txt_command = u'Отменяю изменение исполняемого-файла:'+_object_.path+'-'+ChangeType[_object_.text_status]
                    client.revert(_object_.path)
                except Exception as e:
                    log.InLog(CustID, txt_command, False, str(e),True)
                else:
                    log.InLog(CustID, txt_command, True, u'',False)
                   
    except Exception as e:
        log.InLog(CustID, txt_command, False, str(e),True)

###############################################################
def GetStatusRepository(xdata):
    ###########################################################
    # Статус файлов репозитория
    # Возвращается массив
    # Пусть к объекту, статус   pysvn.wc_status_kind.deleted,
    #                           pysvn.wc_status_kind.added,
    #                           pysvn.wc_status_kind.modified,
    #                           pysvn.wc_status_kind.conflicted,
    #                           pysvn.wc_status_kind.unversioned
    ###########################################################

    pathClient = xdata['LocalRepository']
    _GetStatusRepository={}
    CustID=xdata['Warehouse']
    try:
        txt_command = u'Авторизация к рабочей копии SVN:'+pathClient
        client = pysvn.Client()
        client.set_default_username(xdata['User'])
        client.set_default_password(xdata['Password'])
        client.callback_ssl_server_trust_prompt = callback_ssl_server_trust_prompt
        txt_command = u'Получение статуса локального репозитория:'+pathClient
        changes = client.status(pathClient)
        _GetStatusRepository=changes  
    except Exception as e:
        log.InLog(CustID, txt_command, False, str(e), True)
    else:
        log.InLog(CustID, txt_command, True, u'',False)
        return _GetStatusRepository
        
###############################################################
def ConflictRepository(xdata):
    ###########################################################
    # Решение конфиктов
    ###########################################################

    pathClient = xdata['LocalRepository']
    CustID=xdata['Warehouse']
    try:
        txt_command = u'Авторизация к рабочей копии SVN'
        client = pysvn.Client()
        client.set_default_username(xdata['User'])
        client.set_default_password(xdata['Password'])
        client.callback_ssl_server_trust_prompt = callback_ssl_server_trust_prompt
        status_SVN = GetStatusRepository(xdata)
        
        txt_command = u'Решаем конфликты ревизий с приоритетом рабочей копии'
        r_Conflict=True
        
        for f in status_SVN:          
            if f.text_status== pysvn.wc_status_kind.conflicted:
                txt_command = u'Решение конфликта:'+ f.path
                f_mine=f.path+'.mine'
                if os.path.isfile(f_mine):
                    os.remove(f.path)
                    os.rename(f_mine,f.path)
                    client.resolved(f.path)
                    r_Conflict=False
                else:
                    txt_command = u'Не удалось найти конфликтную версию с рабочей копии файла:'+f_mine
    except Exception as e:
        log.InLog(CustID, txt_command, False, str(e),True)
    else:
        log.InLog(CustID, txt_command, True, u'',False)
    
###############################################################
def IsRepository(xdata):
    ###########################################################
    # Определяет является ли каталог рабочим локальным репозторием
    ###########################################################
    pathClient = xdata['LocalRepository']
    CustID=xdata['Warehouse']
    try:
        txt_command=u'Авторизация к локальной рабочей копии SVN'
        client = pysvn.Client()
        client.set_default_username(xdata['User'])
        client.set_default_password(xdata['Password'])
        client.callback_ssl_server_trust_prompt = callback_ssl_server_trust_prompt
        txt_command=u'Получение информации о локальной рабочей копии SVN'
        entry = client.info(pathClient)
    except Exception as error:
        Res=False
        log.InLog(CustID, txt_command, False , str(error),False)
    else:
        Res=True
        log.InLog(CustID, txt_command, True, '',False)
    return Res
    

###############################################################
def GrandFolders(xdata,path='.',file_rights='0777',folder_rights='0777',test_mode=False,test_status=True): #511 - 0777 права
    ###########################################################
    # Предоставление полных прав к каталогу (рекурсия)
    ###########################################################
    CustID=xdata['Warehouse']

    filerights=int(str(file_rights),8) #Преобразуем из восмиричное число в десятиричное
    folderrights=int(str(folder_rights),8) #Преобразуем из восмиричное число в десятиричное
    
    for object in os.listdir(path):
        _path_=os.path.join(path,object)
        if os.path.isdir(_path_):
            try:
                if not test_mode: txtCommand=u'Изменяем права к каталогу: '+_path_
                else: txtCommand=u'Проверяем права к каталогу: '+_path_
                os.chmod(_path_,folderrights)
                test_status=GrandFolders(xdata,_path_,file_rights,folder_rights,test_mode,test_status)
            except Exception as error:
                test_status=False
                if not test_mode: log.InLog(CustID, txtCommand, False, str(error),False) #Не выводим ошибки на экран
                else: log.InLog(CustID, txtCommand, False, str(error),True)
        else:
            try:    
                if not test_mode: txtCommand=u'Изменяем права к файлу: '+_path_
                else: txtCommand=u'Проверяем права к файлу: '+_path_
                os.chmod(_path_,filerights)
            except Exception as error:
                test_status=False
                if not test_mode: log.InLog(CustID, txtCommand, False, str(error),False) #Не выводим ошибки на экран
                else: log.InLog(CustID, txtCommand, False, str(error),True)
                
    return test_status
    
###############################################################
def RemoveFolder(xdata,path):
    ###########################################################
    # Удаляет каталог .SVN
    ###########################################################    
    
    CustID=xdata['Warehouse']

    if os.path.isdir(path):
        try:
            #Предоставление прав
            txtCommand=u'Изменяем права каталога: '+path
            GrandFolders(xdata,path)
            txtCommand=u'Удаление каталога ' + path
            shutil.rmtree(path)
        except Exception as error:
            log.InLog(CustID, txtCommand, False, str(error),True)
        



def AddFileToSVN(file,mark,comment):
    ##########################################################
    #   Добавляем и обновляем лог в репозиторий
    ##########################################################

    try:
        txt_command = u'Авторизация репозитория SVN'
        client = pysvn.Client()
        client.set_default_username(xdata['User'])
        client.set_default_password(xdata['Password'])
        client.callback_ssl_server_trust_prompt = callback_ssl_server_trust_prompt
        txt_command = u'Проверяем статус наличия файла в репозитории:'+file

        if client.status(file)[0].text_status==pysvn.wc_status_kind.unversioned: client.add(file) #Если не верисифицирован, то добавляем в репозиторий  
        txt_command = u'Отправка '+comment+u' на сервер SVN'
        client.checkin(file, mark+u' * '+comment+u' * '+VERSION)
        res=True
    except Exception as e:
        try:
            # Решение конфликта файла
            for ee in e:
                error=str(ee)
                if error.find('remains in conflict') >= 0:
                    client.resolved(file)                           #Решаем конфликт
                    client.checkin(file, mark+u' * '+comment+u' * '+VERSION )
                    res=True
        except:
            print (CustID, txt_command, str(e))
    return res

def run(logger_arg):

    SVN(logger_arg).run_requests_all()
    logger.info(f'НАЧАЛО: ОБНОВЛЕНИЕ')
    run(logger)
    logger.info(f'КОНЕЦ: ОБНОВЛЕНИЕ')

if __name__ == "__main__":
    # Init interface folder
    init()
    # Init logger
    logger = log.init()
    run(logger)


