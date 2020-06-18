import random
import time
from functools import lru_cache
from threading import Thread

from configs import store

banned_word = {
    "vto.pe": "впо.пе",
    "@all": "<all>",
    "@everyone": "<all>",
    "@тут": "<онлине>",
    "@все": "<алл>",
    "@здесь": "<онлине>",
    "@here": "<онлине>",
    "@online": "<онлине>"
}


def void(target, arg=None, timeout=None):
    if timeout is not None:
        time.sleep(timeout)
    if arg is None:
        arg = []
    try:
        target(*arg)
    except Exception as s:
        print(f"Ошибка в функции {target.__name__}\n"
              f"Аргументы: {arg}\n"
              f"Ошибка: {s}\n"
              f"Отправьте разработчику!")


class Base:
    @staticmethod
    def GetNameUsers(user_ids):
        names = []
        resp = store.bot.api.users.get(user_ids=user_ids)
        for u in resp:
            names.append(f"@id{u['id']}({u['first_name']})")
        return ", ".join(names)

    @staticmethod
    def MessageEdit(mid, t, peer):
        store.bot.api.messages.edit(peer_id=peer,
                                    message_id=mid,
                                    message=t)

    @staticmethod
    def run(target, arg=None, timeout=None):
        if arg is None:
            arg = []
        Thread(target=void, args=[target, arg, timeout], daemon=True).start()

    def MessagesSend(self, _peer_id, _text="", disable_mentions=1, attachment=None, reply_to=None):
        return store.bot.api.messages.send(peer_id=_peer_id,
                                           message=self.ReplaceBannedWord(_text.replace('&lt;', '<')
                                                                          .replace('&gt;', '>')
                                                                          .replace('&quot;', '"')
                                                                          .replace('&amp;', '&')),
                                           random_id=random.randint(-1000000, 1000000),
                                           disable_mentions=disable_mentions,
                                           dont_parse_links=1,
                                           attachment=attachment,
                                           reply_to=reply_to)

    @staticmethod
    def MessageDelete(mid, delete_for_all=1):
        store.bot.api.messages.delete(message_ids=mid,
                                      delete_for_all=delete_for_all)

    @staticmethod
    def ReplaceBannedWord(text):
        for c, v in banned_word.items():
            text = text.replace(c, v)
        return text

    @staticmethod
    @lru_cache(maxsize=32)
    def UploadAudio(src):
        return
