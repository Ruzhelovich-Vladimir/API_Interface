import json

class JsonFile:
    """Json file Class"""

    __slots__ = 'file_pathname'
    def __init__(self, file_pathname):
        self.file_pathname = file_pathname

    @property
    def get_json_data(self):
        with open(self.file_pathname, "r", encoding='utf-8') as read_file:
            data = json.load(read_file)

        return data
