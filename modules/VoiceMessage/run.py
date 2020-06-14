import os
from urllib.request import urlretrieve

from vk_api.longpoll import Event, VkEventType
from vk_api.upload import VkUpload

from configs import store
from utils import Base

store if store.config.get("TriggerAddAudio") else store.add_value("TriggerAddAudio", "!гс")
store if store.config.get("TriggerAudio") else store.add_value("TriggerAudio", ".")
store if store.config.get("audio_cache") else store.add_value("audio_cache", {})
store.save()


def GetLinkAudio(response):
    if response:
        attachments = response.get("attachments")
        for attach in attachments:
            audio_message = attach.get("audio_message")
            if audio_message:
                return audio_message.get("link_ogg")
        return ""


audios = []


def loadAudios():
    for x in os.listdir(f"{os.getcwd()}/example/audios"):
        if x.endswith(".ogg"):
            audios.append(x[:-4])


loadAudios()


class Main(Base):
    __flags__ = {
        VkEventType.MESSAGE_NEW: True,
        VkEventType.MESSAGE_FLAGS_SET: False,
        VkEventType.MESSAGE_EDIT: False
    }

    def __init__(self, event: Event):
        self.disable = False
        self.event = event
        self.upload = VkUpload(store.bot.api)

    def message_new(self):
        if self.event.user_id == store.bot.user_id and self.event.from_chat:
            message: str = self.event.text.lower()
            if message.startswith(store.config.TriggerAddAudio):
                name = message.replace(store.config.TriggerAddAudio, "").strip()
                res = store.bot.api.messages.getById(message_ids=self.event.message_id)["items"]
                get_id = None
                if res:
                    response = res[0]
                    reply_message = response.get("reply_message")
                    fwd_messages = response.get("fwd_messages")
                    if reply_message:
                        get_id = reply_message
                    elif fwd_messages:
                        get_id = fwd_messages[0]
                if get_id is not None and name:
                    url = GetLinkAudio(get_id)
                    if url:
                        urlretrieve(url, f"example/audios/{name}.ogg")
                        self.MessageDelete(self.event.message_id)
                        loadAudios()
                        return
            elif message.startswith(store.config.TriggerAudio):
                message = message.replace(store.config.TriggerAudio, "", 1).strip()
                if message in audios:
                    cached = store.config.audio_cache.get(message)
                    if not cached:
                        cached = self.upload.audio_message(f"{os.getcwd()}/example/audios/{message}.ogg",
                                                           peer_id=self.event.peer_id)
                        audio = cached.get("audio_message")
                        if audio:
                            store.config.audio_cache[
                                message] = f"doc{audio['owner_id']}_{audio['id']}_{audio['access_key']}"
                            store.save()
                    res = store.bot.api.messages.getById(message_ids=self.event.message_id)["items"]
                    reply_to = None
                    if res:
                        response = res[0]
                        reply_message = response.get("reply_message")
                        if reply_message:
                            reply_to = reply_message['id']
                    self.MessagesSend(_peer_id=self.event.peer_id, attachment=store.config.audio_cache.get(message),
                                      reply_to=reply_to)
                    self.MessageDelete(self.event.message_id)

    def message_edit(self):
        return

    def message_delete(self):
        return
