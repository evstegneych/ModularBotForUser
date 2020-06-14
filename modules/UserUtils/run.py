from vk_api.longpoll import Event, VkEventType

from configs import store
from utils import Base

store if store.config.get("TriggerDelete") else store.add_value("TriggerDelete", "ой")
store if store.config.get("TriggerTranslate") else store.add_value("TriggerTranslate", "рас")
store.save()


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
        if self.event.user_id == store.bot.user_id and self.event.from_chat:
            message = self.event.text.lower()
            if message.startswith(store.config.TriggerDelete):
                message_ = message.replace(store.config.TriggerDelete, '')
                if not len(message_):
                    message_ = str(abs(len(message_) + 1))
                if message_.isdigit():
                    res = store.bot.api.messages.getHistory(peer_id=self.event.peer_id)

                    count = 0
                    count_max = int(message_) + 1
                    to_del = []
                    for x in res.get('items', []):
                        if x['from_id'] == store.bot.user_id:
                            to_del.append(x['id'])
                            count += 1
                        if count >= count_max:
                            break
                    if len(to_del) != 0:
                        try:
                            self.MessageDelete(to_del)
                        except Exception as s:
                            print("Удаление сообщения:", s)

            elif message == store.config.TriggerTranslate:
                message_ = store.LastMyMessage.get(self.event.peer_id)
                if message_ is not None:
                    response = store.bot.api.messages.getById(message_ids=message_)
                    msg = response.get("items", [{}])[0]
                    text = msg.get("text")
                    if text is not None:
                        eng_chars = "~!@#%^&qwertyuiop[]asdfghjkl;'zxcvbnm,.QWERTYUIOP{}ASDFGHJKL:\".ZXCVBNM<>"
                        rus_chars = "ё!\"№%:?йцукенгшщзхъфывапролджэячсмитьбюЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭ/ЯЧСМИТЬБЮ"
                        trans_table = dict(zip(eng_chars + rus_chars, rus_chars + eng_chars))
                        swapped_message = ""
                        for c in text:
                            swapped_message += trans_table.get(c, c)
                        try:
                            self.MessageEdit(message_, swapped_message, self.event.peer_id)
                            self.MessageDelete(self.event.message_id)
                        finally:
                            pass
            else:
                store.LastMyMessage.update({self.event.peer_id: self.event.message_id})

    def message_edit(self):
        return

    def message_delete(self):
        return
