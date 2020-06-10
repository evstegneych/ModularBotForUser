import codecs
import json
import shutil
import os
from os.path import isfile


class Config:

    def __init__(self, filename):
        self.filename = self.get_path(filename)
        self._data = {}
        self.check()

    @property
    def data(self):
        return self._data

    @staticmethod
    def get_path(p):
        return f"{os.getcwd()}/configs/{p}"

    def load(self, ):
        with codecs.open(self.filename, "r", "utf-8-sig") as file:
            self._data = json.load(file)

    def save(self):
        if self._data is not None:
            with codecs.open(self.filename, "w", "utf-8-sig") as file:
                json.dump(self._data, file, ensure_ascii=False, indent=4)

    def check(self):
        if isfile('config.json'):
            try:
                shutil.copy(self.get_path('config.json.sample'), self.get_path('config.json'))
                exit("Настрой файл config.json")
            except Exception as s:
                exit("Проверьте ваши права на данную папку!")
                # Чтобы линт не ругался
                print(s)
        else:
            self.load()
            for c, v in self._data.items():
                try:
                    if v == "":
                        raise ValueError
                except AttributeError:
                    self.save()
                    exit("У тебя неправильно настроен конфиг. Перезапусти скрипт и настрой config.json")
                except Exception as s:
                    exit("Заполни все пустые строки в config.json")
                    # Чтобы линт не ругался
                    print(s)

    def add_value(self, attr, value):
        self._data[attr] = value
        self.save()

    def __repr__(self):
        return str(self._data)
