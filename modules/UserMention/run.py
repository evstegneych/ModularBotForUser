import datetime
import random
import re
import time

from vk_api.longpoll import Event, VkEventType

from configs import store
from utils import Base

store if store.config.get("TriggerAddStickers") else store.add_value("TriggerAddStickers", "!+")
store if store.config.get("TriggerIgnoreMention") else store.add_value("TriggerIgnoreMention", "!игнор")
store if store.config.get("TimeWait") else store.add_value("TimeWait", 5)
store if store.config.get("TimeOutDel") else store.add_value("TimeOutDel", 10)
store if store.config.get("Answers") else store.add_value("Answers", [])
store if store.config.get("IgnoreListMention") else store.add_value("IgnoreListMention", [])
store if store.config.get("TriggerStickers") else store.add_value("TriggerStickers", [])
store.save()


def CheckMarkUser(for_finder):
    _for_finder = for_finder.split()
    for x in store.config.TriggerStickers:
        if x.lower() in _for_finder:
            return True
    # if store.config.TriggerStickers:
    #     finder = re.search(rf"(\s+|^)({re.escape('|'.join(store.config.TriggerStickers))})(\s+|$)", for_finder)
    #     if finder is not None:
    #         return True
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
        if self.event.from_chat:
            message = self.event.text.lower()
            find = CheckMarkUser(message)
            if self.event.user_id != store.bot.user_id:
                if find and self.event.peer_id not in store.config.IgnoreListMention:
                    if datetime.datetime.now() >= store.mentionLastFind:
                        if len(store.config.Answers):
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
                                store.mentionLastFind = datetime.datetime.now() + datetime.timedelta(
                                    minutes=store.config.TimeWait)
            else:
                if message == store.config.TriggerIgnoreMention:
                    dialog_id = self.event.peer_id
                    if dialog_id in store.config.IgnoreListMention:
                        store.config.IgnoreListMention.remove(dialog_id)
                        self.MessageEdit(self.event.message_id, f"Диалог <<{dialog_id}>> удален из игнор листа.",
                                         dialog_id)
                    else:
                        store.config.IgnoreListMention.append(self.event.peer_id)
                        self.MessageEdit(self.event.message_id, f"Диалог <<{dialog_id}>> добавлен в игнор лист.",
                                         dialog_id)
                    self.run(self.MessageDelete, arg=[self.event.message_id], timeout=store.config.TimeOutDel)
                    store.save()
                    return

                elif message.startswith(store.config.TriggerAddStickers):
                    sticker_id = None
                    response = store.bot.api.messages.getById(message_ids=self.event.message_id)["items"]
                    if response:
                        response = response[0]
                        get_sticker = response.get("reply_message")
                        if get_sticker is None:
                            get_sticker = response.get("fwd_messages")
                            if get_sticker:
                                get_sticker = get_sticker[0]
                            else:
                                get_sticker = None
                        if get_sticker is not None:
                            attach = get_sticker.get("attachments")
                            if attach:
                                attach = attach[0].get("sticker")
                                if attach is not None:
                                    sticker_id = attach["sticker_id"]
                    if sticker_id is not None:
                        if sticker_id in store.config.Answers:
                            store.config.Answers.remove(sticker_id)
                            self.MessageEdit(self.event.message_id, f"Стикер <<{sticker_id}>> удален.",
                                             self.event.peer_id)
                        else:
                            store.config.Answers.append(sticker_id)
                            self.MessageEdit(self.event.message_id, f"Стикер <<{sticker_id}>> добавлен.",
                                             self.event.peer_id)
                        self.run(self.MessageDelete, arg=[self.event.message_id], timeout=store.config.TimeOutDel)
                        store.save()

    def message_edit(self):
        return

    def message_delete(self):
        return
