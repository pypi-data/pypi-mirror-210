# -*- coding: utf-8 -*-

from mod.common.component.baseComponent import BaseComponent

class ChatExtensionComponentServer(BaseComponent):
    def Enable(self):
        # type: () -> bool
        """
        启用官方聊天扩展功能。需要在ClientLoadAddonsFinishServerEvent事件中调用。仅在联机大厅和网络服中生效。
        """
        pass

    def Disable(self):
        # type: () -> bool
        """
        关闭官方聊天扩展功能。需要在ClientLoadAddonsFinishServerEvent事件中调用。仅在联机大厅和网络服中生效。
        """
        pass

