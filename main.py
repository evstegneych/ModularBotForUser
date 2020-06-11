import os
import sys
import time
import traceback

import vk_api
from requests import ReadTimeout
from vk_api.longpoll import VkLongPoll, VkEventType

from configs import store

modules = []

plugin_folder_files = os.listdir("modules")
if not plugin_folder_files:
    print("Нет установленных модулей.")
    exit()

sys.path.insert(0, "modules")
for file in plugin_folder_files:
    if file.startswith("__") and file.endswith(".py"):
        continue
    try:
        modules.append(__import__(os.path.splitext(file)[0]).Main)
        print(f"Загружен модуль {file}")
    except Exception:
        pass


def main():
    vk_session = vk_api.VkApi(token=store.config.token)
    longpoll = VkLongPoll(vk_session)
    vk = vk_session.get_api()

    user_info = vk.users.get()[0]
    user_id = user_info["id"]
    store.bot.user_id = user_id
    store.bot.api = vk
    user_name = f"{user_info['first_name']} {user_info['last_name']}"

    print(f"{user_name}, Бот запущен")
    while True:
        try:
            for event in longpoll.listen():
                for module in modules:
                    mod = module(event)
                    if not mod.disable:
                        if mod.__flags__.get(event.type):
                            if event.type == VkEventType.MESSAGE_NEW:
                                mod.message_new()

                            if event.type == VkEventType.MESSAGE_FLAGS_SET and event.raw[2] & 131072:
                                mod.message_delete()

                            if event.type == VkEventType.MESSAGE_EDIT:
                                mod.message_edit()
        except ReadTimeout:
            pass

        except Exception as e:
            print("Основной поток:\n", traceback.format_exc())
            time.sleep(10)


if __name__ == '__main__':
    main()
