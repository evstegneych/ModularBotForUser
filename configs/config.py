import codecs
import json
import os
import shutil
from os.path import isfile

from objdict import ObjDict


class Config:
    def __init__(self, filename):
        self.filename = self.get_path(filename)
        self.bot = ObjDict()
        self.config = ObjDict()
        self.check()

        # for modules
        self.messages = {}

    @staticmethod
    def get_path(p):
        return f"{os.getcwd()}/configs/{p}"

    def load(self, ):
        with codecs.open(self.filename, "r", "utf-8-sig") as file:
            self.config = ObjDict(json.load(file))

    def save(self):
        with codecs.open(self.filename, "w", "utf-8-sig") as file:
            json.dump(self.config, file, ensure_ascii=False, indent=4)

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
            for c, v in self.config.items():
                try:
                    if v == "":
                        raise ValueError
                except AttributeError:
                    exit("У тебя неправильно настроен конфиг. Перезапусти скрипт и настрой config.json")
                except Exception as s:
                    exit("Заполни все пустые строки в config.json")
                    # Чтобы линт не ругался
                    print(s)

    def add_value(self, attr, value):
        self.config.update({attr: value})

    # def del_value(self, attr):
    #     self.config

    def __repr__(self):
        return str(self.config.items())
