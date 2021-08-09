from config.config import settings
import os



def init():

    # Creating interface folders
    dir_ls = (
        settings.SCHEMES_JSON_DATA_FOLDER, settings.ARCHIVES_FOLDER, settings.CONF_FILENAME, settings.OUTBOX_DATA_FOLDER,
        settings.INBOX_DATA_FOLDER, settings.ARCHIVE_OUTBOX_DATA_FOLDER, settings.ARCHIVE_INBOX_DATA_FOLDER,
        settings.ERRORS_FOLDER)

    for path in dir_ls:
        try:
            os.makedirs(path)
        except:
            pass

    # # Clearing error folder
    # lst = os.listdir(settings.ERRORS_FOLDER)
    # for file_name in lst:
    #     if file_name.endswith(f'.json'):
    #         os.remove(os.path.join(settings.ERRORS_FOLDER, file_name))


