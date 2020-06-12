import datetime
import random
import re
import time

from vk_api.longpoll import Event, VkEventType

from configs import store
from utils import Base

store if store.config.get("TimeWait") else store.add_value("TimeWait", 5)
store if store.config.get("Answers") else store.add_value("Answers", [])
store if store.config.get("IgnoreList") else store.add_value("IgnoreList", [])
store if store.config.get("TriggerStickers") else store.add_value("TriggerStickers", [])
store.save()


def CheckMarkUser(for_finder):
    finder = re.search(rf"(\s+|^)({'|'.join(store.config.TriggerStickers)})(\s+|$)", for_finder)
    if finder is not None:
        return True
    finder = re.search(rf"\[id{store.bot.user_id}\|(?:|@).{{2,15}}\]", for_finder)
    if finder is not None:
        return True
    return False


class Main(Base):
    __flags__ = {
        VkEventType.MESSAGE_NEW: True,
        VkEventType.MESSAGE_FLAGS_SET: False,
        VkEventType.MESSAGE_EDIT: False
    }

    def __init__(self, event: Event):
        self.disable = False
        self.event = event

    def message_new(self):
        find = CheckMarkUser(self.event.text.lower())
        if (
                find
                and self.event.user_id != store.bot.user_id
                and self.event.peer_id not in store.config.IgnoreList
        ):

            if datetime.datetime.now() >= store.mentionLastFind:
                choice_msg = random.choice(store.config.Answers)
                try:
                    time.sleep(.3)
                    if isinstance(choice_msg, int):
                        store.bot.api.messages.send(peer_id=self.event.peer_id, sticker_id=choice_msg,
                                                    random_id=random.randint(-1000000, 1000000))
                    else:
                        store.bot.api.messages.send(peer_id=self.event.peer_id, message=choice_msg,
                                                    random_id=random.randint(-1000000, 1000000))
                except Exception as s:
                    print("Отправка сообещния на упоминание:", s)
                finally:
                    store.mentionLastFind = datetime.datetime.now() + datetime.timedelta(minutes=store.config.TimeWait)

    def message_edit(self):
        return

    def message_delete(self):
        return
