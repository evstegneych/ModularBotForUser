import datetime

from vk_api.longpoll import Event, VkEventType

from configs import store
from utils import Base

store if store.config.get("TriggerShowLog") else store.add_value("TriggerShowLog", "!лог")
store if store.config.get("TriggerToAddChatLogs") else store.add_value("TriggerToAddChatLogs", "!добавить чат")
store if store.config.get("TriggerShowChatsLogs") else store.add_value("TriggerShowChatsLogs", "!все чаты")
store if store.config.get("WhiteListChat") else store.add_value("WhiteListChat", [])
store.save()


class Message:
    def __init__(self, _user_id, _peer_id, _message_id):
        self.user_id = _user_id
        self.peer_id = _peer_id
        self.access = self.peer_id in store.config.WhiteListChat
        self.name = Base.GetNameUsers(self.user_id) + ":"
        self._text = ""
        self.attachments = []
        self.message_id = _message_id
        self.date = datetime.datetime.now().strftime("[%H:%M:%S]")
        self.deleted = False
        self.edited = False
        self.count_edited = 0
        self.audio = False

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = value

    @text.getter
    def text(self):
        if self.access:
            return self._text
        else:
            if self._text:
                return self._text
            else:
                return "[Вложение]"

    def set_deleted(self):
        self.deleted = True

    def get_deleted(self):
        return "[deleted]" if self.deleted else ""

    def set_edited(self):
        self.edited = True

    def get_edited(self):
        return "[edited]\n" if self.edited else " "

    def set_audio(self):
        self.audio = True

    def __repr__(self):
        return f"{self.user_id}:{self.peer_id}:{self.message_id}"


def GetAllAttachments(msg: Message):
    response = store.bot.api.messages.getById(message_ids=msg.message_id)["items"]
    if response:
        response = response[0]
        attachments = response.get("attachments")
        _arr = []
        if not msg.attachments:
            msg.attachments = []
        for attach in attachments:
            audio_message = attach.get("audio_message")
            if audio_message:
                msg.attachments.append(audio_message.get("link_ogg"))
                msg.set_audio()
                break

            sticker = attach.get("sticker")
            if sticker:
                msg.attachments.append(sticker["images"][len(sticker["images"]) - 1]["url"])

            photo = attach.get("photo")
            if photo:
                msg.attachments.append(photo["sizes"][len(photo["sizes"]) - 1]["url"])

            video = attach.get("video")
            if video:
                msg.attachments.append(f"https://vk.com/video{video['owner_id']}_{video['id']}")

            audio = attach.get("audio")
            if audio:
                msg.attachments.append(f"Музыка: {audio['artist']} -- {audio['title']}")
    return msg


class Main(Base):
    __flags__ = {
        VkEventType.MESSAGE_NEW: True,
        VkEventType.MESSAGE_FLAGS_SET: True,
        VkEventType.MESSAGE_EDIT: True
    }

    def __init__(self, event: Event):
        self.disable = False
        self.event = event

    def message_new(self):
        if self.event.from_chat and self.event.user_id > 0:
            if self.event.user_id != store.bot.user_id:
                msg = Message(self.event.user_id, self.event.peer_id, self.event.message_id)
                if self.event.peer_id not in store.messages:
                    store.messages[self.event.peer_id] = []
                if self.event.text:
                    msg.text = self.event.text[:150]
                else:
                    if msg.access:
                        msg = GetAllAttachments(msg)
                _len = len(store.messages[self.event.peer_id])
                if _len > 500:
                    store.messages[self.event.peer_id] = store.messages[self.event.peer_id][_len - 250:]
                store.messages[self.event.peer_id].append(msg)
            else:
                if not self.event.text:
                    return
                message = self.event.message.lower()

                if message.startswith(store.config.TriggerShowLog):
                    cmd = message[len(store.config.TriggerShowLog):].strip()
                    show_only_deleted = cmd == "+"
                    response = store.bot.api.messages.getById(message_ids=self.event.message_id)["items"]
                    get_user_id = None
                    if response:
                        response = response[0]
                        reply_message = response.get("reply_message")
                        fwd_messages = response.get("fwd_messages")
                        if reply_message:
                            get_user_id = reply_message["from_id"]
                        elif fwd_messages:
                            get_user_id = fwd_messages[0]["from_id"]

                    text = f"Лог {self.GetNameUsers(get_user_id) if get_user_id else ''}:\n"
                    arr = store.messages.get(self.event.peer_id, [])
                    logs = []
                    for user in arr:
                        if user.user_id == get_user_id or not get_user_id:
                            if (show_only_deleted and user.deleted) or not show_only_deleted:
                                logs.append(user)
                    lastUser = 0
                    logs = logs if len(logs) < 10 else logs[len(logs) - 10:]
                    for user in logs:
                        a = "Вложения:\n " + "\n".join(list(set(user.attachments))) + "\n"
                        if get_user_id or (lastUser == user.user_id):
                            name = ""
                        else:
                            name = user.name + "\n"
                        lastUser = user.user_id
                        text += f"{name}{user.date} -- {user.get_edited()}" \
                                f"{user.get_deleted()} {user.text}\n" \
                                f"{a if user.attachments else ''}" \
                                f"{'' if get_user_id else ''}"
                    self.MessagesSend(self.event.peer_id, text)
                    self.MessageDelete(self.event.message_id)

                if message == store.config.TriggerToAddChatLogs:
                    if self.event.peer_id in store.config.WhiteListChat:
                        store.config.WhiteListChat.remove(self.event.peer_id)
                        self.MessageEdit(self.event.message_id, f"Беседа <<{self.event.peer_id}>> удалена.",
                                         self.event.peer_id)
                    else:
                        store.config.WhiteListChat.append(self.event.peer_id)
                        self.MessageEdit(self.event.message_id, f"Беседа <<{self.event.peer_id}>> добавлена.",
                                         self.event.peer_id)
                    self.run(target=self.MessageDelete, arg=[self.event.message_id], timeout=5)
                    store.save()

                if message == store.config.TriggerShowChatsLogs:
                    chats = "\n".join(
                        list(
                            map(lambda x: f"{x} {'✅' if self.event.peer_id == x else ''}", store.config.WhiteListChat)))
                    self.MessageEdit(self.event.message_id,
                                     f"Все чаты в которых включено получение вложений:\n {chats}", self.event.peer_id)
                    self.run(target=self.MessageDelete, arg=[self.event.message_id], timeout=10)

    def message_edit(self):
        if self.event.peer_id in store.messages:
            for user in store.messages.get(self.event.peer_id, []):
                if user.message_id == self.event.message_id and not user.audio and user.count_edited <= 4:
                    if user.access:
                        user = GetAllAttachments(user)
                    user.text += f"\n↓\n{self.event.text[:100]}"
                    user.edited = True
                    user.count_edited += 1
                if user.count_edited == 5:
                    user.text += f"\n[Редактирований > 5]"

    def message_delete(self):
        if self.event.peer_id in store.messages:
            for user in store.messages.get(self.event.peer_id, []):
                if user.message_id == self.event.message_id:
                    user.set_deleted()
