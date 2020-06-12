from vk_api.longpoll import Event, VkEventType

from configs import store
from utils import Base


class Main(Base):
    __flags__ = {
        VkEventType.MESSAGE_NEW: True,
        VkEventType.MESSAGE_FLAGS_SET: False,
        VkEventType.MESSAGE_EDIT: False
    }

    def __init__(self, event: Event):
        self.disable = False
        self.event = event
        self.user = self.event.user_id = store.bot.user_id

    def message_new(self):
        return

    def message_edit(self):
        return

    def message_delete(self):
        return
