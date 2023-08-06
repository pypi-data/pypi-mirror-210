#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from asyncio import Lock as ALock
from asyncio import get_event_loop, new_event_loop
from importlib.machinery import SourceFileLoader
from os import getpid
from os.path import exists
from os.path import split as path_split
from re import Pattern
from threading import Lock as TLock
from time import sleep as t_sleep
from typing import Any, Callable, Iterable, List, Optional, Union

from . import _exception
from ._api_model import robot_model
from ._session import SessionManager
from ._utils import func_type_checker
from .api import API
from .async_api import AsyncAPI
from .http import Session
from .logger import Logger
from .model import BotCommandObject, Model
from .plugins import Plugins
from .qg_bot_ws import BotWs as _BotWs
from .session import AbstractSessionManager, SessionPatcher
from .version import __version__

pid = getpid()
print(f"本次程序进程ID：{pid} | SDK版本：{__version__} | 即将开始运行机器人……")
t_sleep(0.5)
json.JSONEncoder.default = lambda self, obj: (
    obj.__json__() if hasattr(obj, "__json__") else str(obj)
)


class BOT:
    def __init__(
        self,
        bot_id: str,
        bot_token: str,
        bot_secret: Optional[str] = None,
        is_private: bool = False,
        is_sandbox: bool = False,
        no_permission_warning: bool = True,
        is_async: bool = False,
        is_retry: bool = True,
        is_log_error: bool = True,
        shard_no: int = 0,
        total_shard: int = 1,
        max_workers: int = 32,
        api_max_concurrency: int = 0,
        api_timeout: int = 20,
        disable_reconnect_on_not_recv_msg: float = 1000,
    ):
        """
        机器人主体，输入BotAppID和密钥，并绑定函数后即可快速使用

        :param bot_id: 机器人平台后台BotAppID（开发者ID）项，必填
        :param bot_token: 机器人平台后台机器人令牌项，必填
        :param bot_secret: 机器人平台后台机器人密钥项（已废弃）
        :param is_private: 机器人是否为私域机器人，默认False
        :param is_sandbox: 是否开启沙箱环境，默认False
        :param no_permission_warning: 是否开启当机器人获取疑似权限不足的事件时的警告提示，默认开启
        :param is_async: 使用同步api还是异步api，默认False（使用同步）
        :param is_retry: 使用api时，如遇可重试的错误码是否自动进行重试，默认开启
        :param is_log_error: 使用api时，如返回的结果为不成功，可自动log输出报错信息，默认开启
        :param shard_no: 当前分片数，如不熟悉相关配置请不要轻易改动此项，默认0
        :param total_shard: 最大分片数，如不熟悉相关配置请不要轻易改动此项，默认1
        :param max_workers: 在同步模式下，允许同时运行的最大线程数，默认32
        :param api_max_concurrency: API允许的最大并发数，超过此并发数将进入队列，如此数值<=0代表不开启任何队列，默认0
        :param api_timeout: API请求的超时设置。默认20
        :param disable_reconnect_on_not_recv_msg: 当机器人长时间未收到消息后进行连接而非重连。默认1000秒
        """
        self.logger = Logger(bot_id)
        self.bot_id = bot_id
        self.bot_token = bot_token
        if bot_secret:
            raise DeprecationWarning(
                "bot_secret已被废弃，如需使用安全接口，请通过security_setup()绑定小程序ID和secret"
            )
        self.is_private = is_private
        if is_sandbox:
            self.logger.info(
                "已开启沙箱环境，发送消息时将频道方将自动添加[sandbox]字样，如需关闭请传参is_sandbox=False"
            )
            self.bot_url = r"https://sandbox.api.sgroup.qq.com"
        else:
            self.bot_url = r"https://api.sgroup.qq.com"
        if not bot_id or not bot_token:
            raise _exception.IdTokenMissing(
                "你还没有输入 bot_id 和 bot_token，无法连接使用机器人\n如尚未有相关票据，"
                "请参阅 https://qg-botsdk.readthedocs.io/zh_CN/latest/quick_start 了解相关详情"
            )
        try:
            self._loop = get_event_loop()
        except RuntimeError:
            self._loop = new_event_loop()
        self._intents = 0
        self._shard_no = shard_no
        self._total_shard = total_shard
        self._bot_class = None
        self._func_registers = {}
        self._repeat_function = None
        self._on_start_function = None
        self.del_is_filter_self = True
        self.check_interval = 10
        self.__running = False
        self.__await_closure = False
        self.auth = f"Bot {bot_id}.{bot_token}"
        self.bot_headers = {"Authorization": self.auth}
        self._http_session = Session(
            self._loop,
            is_retry,
            is_log_error,
            self.logger,
            api_max_concurrency,
            api_timeout,
            headers=self.bot_headers,
        )
        self.msg_treat = True
        self.dm_treat = False
        self.no_permission_warning = no_permission_warning
        self.max_workers = max_workers
        self.is_async = is_async
        self.__session_manager = SessionManager(self.logger)
        self.api: Union[AsyncAPI, API] = AsyncAPI(
            self.bot_url,
            self._http_session,
            self.logger,
            self._check_warning,
            self.__session_manager,
        )
        if not is_async:
            self.lock = TLock()
            self.api = API(
                self.api,
                self._loop,
                api_timeout,
                self.__session_manager,
            )
        else:
            self.lock = ALock()
        self.__task = None
        self._commands: List[BotCommandObject] = []
        self._preprocessors: List[Callable[[Model.MESSAGE], Any]] = []
        self.session: AbstractSessionManager = SessionPatcher()
        self.disable_reconnect_on_not_recv_msg = disable_reconnect_on_not_recv_msg

    def __repr__(self):
        return f"<qg_botsdk.BOT object [id: {self.bot_id}, token: {self.bot_token}]>"

    @property
    def robot(self) -> robot_model():
        return self._bot_class.robot

    @property
    def running(self):
        return self.__running

    @property
    def loop(self):
        return self._loop

    def load_default_msg_logger(self):
        """
        加载默认的消息日志模块，可以默认格式自动log记录接收到的用户消息
        """
        self.logger.info("加载默认消息日志模块成功")
        if "__sdk_default_logger" in Plugins.get_preprocessor_names():
            return

        def __sdk_default_logger(data: Model.MESSAGE):
            self.logger.info(
                f"收到频道 {data.guild_id} 用户 {data.author.username}({data.author.id}) "
                f"的消息：{data.treated_msg}"
            )

        Plugins.before_command()(__sdk_default_logger)

    def __register_msg_intents(self, is_log=True):
        if not self._intents >> 9 & 1 and not self._intents >> 30 & 1:
            if self.is_private:
                self._intents = self._intents | 1 << 9
                if is_log:
                    self.logger.info("消息（所有消息）接收函数订阅成功")
            else:
                self._intents = self._intents | 1 << 30
                if is_log:
                    self.logger.info("消息（艾特消息）接收函数订阅成功")

    def _retrieve_new_plugins(self):
        commands, preprocessors = Plugins()
        if commands:
            for items in commands:
                func_type_checker(items.func, Model.MESSAGE, is_async=self.is_async)
            self.__register_msg_intents()
        for func in preprocessors:
            func_type_checker(func, Model.MESSAGE, is_async=self.is_async)
        return commands, preprocessors

    def refresh_plugins(self):
        commands, preprocessors = self._retrieve_new_plugins()
        self._commands.extend(commands)
        self._preprocessors.extend(preprocessors)

    def clear_current_plugins(self):
        self._commands.clear()
        self._preprocessors.clear()

    def remove_command(self, command_obj: BotCommandObject):
        if command_obj in self._commands:
            self._commands.remove(command_obj)
        else:
            raise ValueError(f"未找到指定的command {command_obj}")

    def remove_preprocessors(self, preprocessor: Callable[[Model.MESSAGE], Any]):
        if preprocessor in self._preprocessors:
            self._preprocessors.remove(preprocessor)
        else:
            raise ValueError(f"未找到指定的preprocessor {preprocessor}")

    @property
    def get_current_commands(self) -> List[BotCommandObject]:
        return self._commands[:]

    @property
    def get_current_preprocessors(self) -> List[Callable[[Model.MESSAGE], Any]]:
        return self._preprocessors[:]

    def load_plugins(self, path_to_plugins: str):
        """
        用于加载插件的.py程序

        :param path_to_plugins: 指向相应.py插件文件的相对或绝对路径
        :return:
        """
        if not exists(path_to_plugins):
            raise ModuleNotFoundError(f"指向plugin的路径 [{path_to_plugins}] 并不存在")
        if not path_to_plugins.endswith(".py"):
            path_to_plugins += ".py"
        _name = path_split(path_to_plugins)[1][:-3]
        try:
            SourceFileLoader(_name, path_to_plugins).load_module()
        except Exception:
            raise ImportError(f"plugin [{path_to_plugins}] 导入失败")
        if self._bot_class and self._bot_class.running:
            self.refresh_plugins()

    def before_command(self):
        """
        注册预处理器，将在检查所有commands前执行
        """

        def wrap(func: Callable[[Model.MESSAGE], Any]):
            Plugins.before_command()(func)
            if self._bot_class and self._bot_class.running:
                self.refresh_plugins()
            return func

        return wrap

    def on_command(
        self,
        command: Optional[Union[Iterable[str], str]] = None,
        regex: Optional[Union[Pattern, str, Iterable[Union[Pattern, str]]]] = None,
        is_treat: bool = True,
        is_require_at: bool = False,
        is_short_circuit: bool = True,
        is_custom_short_circuit: bool = False,
        is_require_admin: bool = False,
        admin_error_msg: Optional[str] = None,
    ):
        """
        指令装饰器。用于快速注册消息事件，当连同bind_msg使用时，如没有触发短路，bind_msg注册的函数将在最后被调用

        :param command: 可触发事件的指令列表，与正则regex互斥，优先使用此项
        :param regex: 可触发指令的正则compile实例或正则表达式，与指令表互斥
        :param is_treat: 是否在treated_msg中同时处理指令，如正则将返回.groups()，默认是
        :param is_require_at: 是否要求必须艾特机器人才能触发指令，默认否
        :param is_short_circuit: 如果触发指令成功是否短路不运行后续指令（将根据注册顺序排序指令的短路机制），默认是
        :param is_custom_short_circuit: 如果触发指令成功而回调函数返回True则不运行后续指令，存在时优先于is_short_circuit，默认否
        :param is_require_admin: 是否要求频道主或或管理才可触发指令，默认否
        :param admin_error_msg: 当is_require_admin为True，而触发用户的权限不足时，如此项不为None，返回此消息并短路；否则不进行短路
        """

        def wrap(callback: Callable[[Model.MESSAGE], Any]):
            Plugins.on_command(
                command,
                regex,
                is_treat,
                is_require_at,
                is_short_circuit,
                is_custom_short_circuit,
                is_require_admin,
                admin_error_msg,
            )(callback)
            if self._bot_class and self._bot_class.running:
                self.refresh_plugins()
            return callback

        return wrap

    def bind_msg(
        self,
        callback: Callable[[Model.MESSAGE], Any] = None,
        treated_data: bool = True,
        all_msg: bool = None,
    ):
        """
        用作绑定接收消息的函数，将根据机器人是否公域自动判断接收艾特或所有消息

        :param callback: 类型为function，该回调函数应包含一个参数以接收Object消息数据进行处理
        :param treated_data: 是否返回经转义处理的文本，如是则会在返回的Object中添加一个treated_msg的子类，默认True
        :param all_msg: 是否无视公私域限制，强制开启全部消息接收，默认None（不判断此项参数）
        """

        def wraps(func):
            func_type_checker(func, Model.MESSAGE, is_async=self.is_async)
            self._func_registers["on_msg"] = func
            if not treated_data:
                self.msg_treat = False
            if all_msg is None:
                self.__register_msg_intents()
            elif all_msg:
                self._intents = self._intents | 1 << 9
                self.logger.info("消息（所有消息）接收函数订阅成功")
            else:
                self._intents = self._intents | 1 << 30
                self.logger.info("消息（艾特消息）接收函数订阅成功")

        if not callback:
            return wraps
        wraps(callback)

    def bind_dm(
        self,
        callback: Callable[[Model.DIRECT_MESSAGE], Any] = None,
        treated_data: bool = True,
    ):
        """
        用作绑定接收私信消息的函数

        :param callback: 类型为function，该回调函数应包含一个参数以接收Object消息数据进行处理
        :param treated_data: 是否返回经转义处理的文本，如是则会在返回的Object中添加一个treated_msg的子类，默认True
        """

        def wraps(func):
            func_type_checker(func, Model.DIRECT_MESSAGE, is_async=self.is_async)
            self._func_registers["on_dm"] = func
            self._intents = self._intents | 1 << 12
            self.dm_treat = treated_data
            self.logger.info("私信接收函数订阅成功")

        if not callback:
            return wraps
        wraps(callback)

    def bind_msg_delete(
        self,
        callback: Callable[[Model.MESSAGE_DELETE], Any] = None,
        is_filter_self: bool = True,
    ):
        """
        用作绑定接收消息撤回事件的回调函数，注册时将自动根据公域私域注册艾特或全部消息，但不会主动注册私信事件

        :param callback:类型为function，该回调函数应包含一个参数以接收Object消息数据进行处理
        :param is_filter_self: 是否过滤用户自行撤回的消息，只接受管理撤回事件
        """

        def wraps(func):
            func_type_checker(func, Model.MESSAGE_DELETE, is_async=self.is_async)
            self._func_registers["on_delete"] = func
            self._func_registers["del_is_filter_self"] = is_filter_self
            self.__register_msg_intents(False)
            self.logger.info("撤回事件订阅成功")

        if not callback:
            return wraps
        wraps(callback)

    def bind_guild_event(self, callback: Callable[[Model.GUILDS], Any] = None):
        """
        用作绑定接收频道信息的函数

        :param callback: 类型为function，该回调函数应包含一个参数以接收Object消息数据进行处理
        """

        def wraps(func):
            func_type_checker(func, Model.GUILDS, is_async=self.is_async)
            self._func_registers["on_guild_event"] = func
            self._intents = self._intents | 1
            self.logger.info("频道事件订阅成功")

        if not callback:
            return wraps
        wraps(callback)

    def bind_channel_event(self, callback: Callable[[Model.CHANNELS], Any] = None):
        """
        用作绑定接收子频道信息的函数

        :param callback: 类型为function，该回调函数应包含一个参数以接收Object消息数据进行处理
        """

        def wraps(func):
            func_type_checker(func, Model.CHANNELS, is_async=self.is_async)
            self._func_registers["on_channel_event"] = func
            self._intents = self._intents | 1
            self.logger.info("子频道事件订阅成功")

        if not callback:
            return wraps
        wraps(callback)

    def bind_guild_member(self, callback: Callable[[Model.GUILD_MEMBERS], Any] = None):
        """
        用作绑定接收频道成员信息的函数

        :param callback: 类型为function，该回调函数应包含一个参数以接收Object消息数据进行处理
        """

        def wraps(func):
            func_type_checker(func, Model.GUILD_MEMBERS, is_async=self.is_async)
            self._func_registers["on_guild_member"] = func
            self._intents = self._intents | 1 << 1
            self.logger.info("频道成员事件订阅成功")

        if not callback:
            return wraps
        wraps(callback)

    def bind_reaction(self, callback: Callable[[Model.REACTION], Any] = None):
        """
        用作绑定接收表情表态信息的函数

        :param callback: 类型为function，该回调函数应包含一个参数以接收Object消息数据进行处理
        """

        def wraps(func):
            func_type_checker(func, Model.REACTION, is_async=self.is_async)
            self._func_registers["on_reaction"] = func
            self._intents = self._intents | 1 << 10
            self.logger.info("表情表态事件订阅成功")

        if not callback:
            return wraps
        wraps(callback)

    def bind_interaction(self, callback: Callable[[Model.INTERACTION], Any] = None):
        """
        用作绑定接收互动事件的回调函数

        :param callback: 类型为function，该回调函数应包含一个参数以接收Object消息数据进行处理
        """

        def wraps(func):
            func_type_checker(func, Model.INTERACTION, is_async=self.is_async)
            self._func_registers["on_interaction"] = func
            self._intents = self._intents | 1 << 26
            self.logger.info("互动事件订阅成功")

        if not callback:
            return wraps
        wraps(callback)

    def bind_audit(self, callback: Callable[[Model.MESSAGE_AUDIT], Any] = None):
        """
        用作绑定接收审核事件的回调函数

        :param callback: 类型为function，该回调函数应包含一个参数以接收Object消息数据进行处理
        """

        def wraps(func):
            func_type_checker(func, Model.MESSAGE_AUDIT, is_async=self.is_async)
            self._func_registers["on_audit"] = func
            self._intents = self._intents | 1 << 27
            self.logger.info("审核事件订阅成功")

        if not callback:
            return wraps
        wraps(callback)

    def bind_forum(self, callback: Callable[[Model.FORUMS_EVENT], Any] = None):
        """
        用作绑定接收论坛事件的回调函数，一般仅私域机器人能注册此事件

        .. note::
            当前仅可以接收FORUM_THREAD_CREATE、FORUM_THREAD_UPDATE、FORUM_THREAD_DELETE三个事件

        :param callback: 类型为function，该回调函数应包含一个参数以接收Object消息数据进行处理
        """

        def wraps(func):
            func_type_checker(func, Model.FORUMS_EVENT, is_async=self.is_async)
            self._func_registers["on_forum"] = func
            self._intents = self._intents | 1 << 28
            self.logger.info("论坛事件订阅成功")
            if not self.is_private and self.no_permission_warning:
                self.logger.warning("请注意，一般公域机器人并不能注册论坛事件，请检查自身是否拥有相关权限")

        if not callback:
            return wraps
        wraps(callback)

    def bind_open_forum(self, callback: Callable[[Model.OPEN_FORUMS], Any] = None):
        """
        用作绑定接收公域论坛事件的回调函数

        .. note::
            当前仅可以接收OPEN_FORUM_THREAD_CREATE、OPEN_FORUM_THREAD_UPDATE、OPEN_FORUM_THREAD_DELETE三个事件

        :param callback: 类型为function，该回调函数应包含一个参数以接收Object消息数据进行处理
        """

        def wraps(func):
            func_type_checker(func, Model.OPEN_FORUMS, is_async=self.is_async)
            self._func_registers["on_open_forum"] = func
            self._intents = self._intents | 1 << 18
            self.logger.info("论坛事件订阅成功")

        if not callback:
            return wraps
        wraps(callback)

    def bind_audio(self, callback: Callable[[Model.AUDIO_ACTION], Any] = None):
        """
        用作绑定接收论坛事件的回调函数

        :param callback: 类型为function，该回调函数应包含一个参数以接收Object消息数据进行处理
        """

        def wraps(func):
            func_type_checker(func, Model.AUDIO_ACTION, is_async=self.is_async)
            self._func_registers["on_audio"] = func
            self._intents = self._intents | 1 << 29
            self.logger.info("音频事件订阅成功")
            if self.no_permission_warning:
                self.logger.warning("请注意，一般机器人并不能注册音频事件（需先进行申请），请检查自身是否拥有相关权限")

        if not callback:
            return wraps
        wraps(callback)

    def bind_live_channel_member(
        self,
        callback: Callable[[Model.LIVE_CHANNEL_MEMBER], Any] = None,
    ):
        """
        用作绑定接收音视频/直播子频道成员进出事件的回调函数

        :param callback: 类型为function，该回调函数应包含一个参数以接收Object消息数据进行处理
        """

        def wraps(func):
            func_type_checker(func, Model.LIVE_CHANNEL_MEMBER, is_async=self.is_async)
            self._func_registers["on_live_channel_member"] = func
            self._intents = self._intents | 1 << 19
            self.logger.info("音视频/直播子频道成员进出事件订阅成功")

        if not callback:
            return wraps
        wraps(callback)

    def register_repeat_event(
        self,
        time_function: Callable[[], Any] = None,
        check_interval: Union[float, int] = 10,
    ):
        """
        用作注册重复事件的回调函数，注册并开始机器人后，会根据间隔时间不断调用该回调函数

        :param time_function: 类型为function，该函数不应包含任何参数
        :param check_interval: 每多少秒检查调用一次时间事件函数，默认10
        """

        def wraps(func):
            func_type_checker(func, is_async=self.is_async)
            self._repeat_function = func
            self.check_interval = check_interval
            self.logger.info("重复运行事件注册成功")

        if not time_function:
            return wraps
        wraps(time_function)

    def register_start_event(self, on_start_function: Callable[[], Any] = None):
        """
        用作注册机器人开始时运行的函数，此函数不应有无限重复的内容，会在机器人完成登录后调用该回调函数

        :param on_start_function: 类型为function，该函数不应包含任何参数
        """

        def wraps(func):
            func_type_checker(func, is_async=self.is_async)
            self._on_start_function = func
            self.logger.info("初始事件注册成功")

        if not on_start_function:
            return wraps
        wraps(on_start_function)

    def security_setup(self, mini_id: str, mini_secret: str):
        """
        用于注册小程序ID和secret以使用腾讯内容安全接口

        :param mini_id: 小程序ID
        :param mini_secret: 小程序secret
        """
        self.api.security_setup(mini_id, mini_secret)

    def _check_warning(self, name: str):
        if not self.is_private and self.no_permission_warning:
            self.logger.warning(f"请注意，一般公域机器人并不能使用{name}API，请检查自身是否拥有相关权限")

    def start(self, is_blocking: bool = True):
        """
        开始运行机器人的函数，在唤起此函数后的代码将不能运行，如需非阻塞性运行，请传入is_blocking=False，以下是一个简单的唤起流程：

        >>> from qg_botsdk import BOT
        >>> bot = BOT(bot_id='xxx', bot_token='xxx')
        >>> bot.start()

        .. seealso::
            更多教程和相关资讯可参阅：
            https://qg-botsdk.readthedocs.io/zh_CN/latest/index.html

        :param is_blocking: 机器人是否阻塞运行，如选择False，机器人将以异步任务的方式非阻塞性运行，如不熟悉异步编程请不要使用此项
        """
        try:
            if not self.__running and not self._bot_class:
                self.__running = True
                gateway = self._loop.run_until_complete(
                    self._http_session.get(f"{self.bot_url}/gateway/bot")
                )
                gateway = self._loop.run_until_complete(gateway.json())
                url = gateway.get("url")
                if not url:
                    raise _exception.IdTokenError(
                        "你输入的 bot_id 和/或 bot_token 错误，无法连接使用机器人\n如尚未有相关票据，"
                        "请参阅 https://qg-botsdk.readthedocs.io/zh_CN/latest/quick_start 了解相关详情"
                    )
                self.logger.debug("[机器人ws地址] " + url)
                self.refresh_plugins()
                self._bot_class = _BotWs(
                    self._loop,
                    self._http_session,
                    self.logger,
                    self._total_shard,
                    self._shard_no,
                    url,
                    self.auth,
                    self._func_registers,
                    self._intents,
                    self.msg_treat,
                    self.dm_treat,
                    self._on_start_function,
                    self.check_interval,
                    self._repeat_function,
                    self.is_async,
                    self.max_workers,
                    self.api,
                    self._commands,
                    self._preprocessors,
                    self.disable_reconnect_on_not_recv_msg,
                    self.__session_manager,
                )
                self.__task = self._loop.create_task(self._bot_class.starter())
                if is_blocking and not self._loop.is_running():
                    self._loop.run_until_complete(self.__task)
            else:
                self.logger.error("当前机器人已在运行中！")
        except KeyboardInterrupt:
            self.logger.info("结束运行机器人（KeyboardInterrupt）")
            exit()

    def block(self):
        """
        当BOT.start()选择is_blocking=False的非阻塞性运行时，此函数能在后续阻塞主进程而继续运行机器人
        """
        try:
            if self.__running or self.__await_closure:
                if self.__task and not self._loop.is_running():
                    self._loop.run_until_complete(self.__task)
                    return
            self.logger.error("当前机器人没有运行！")
        except KeyboardInterrupt:
            self.logger.info("结束运行机器人（KeyboardInterrupt）")
            exit()

    def close(self):
        """
        结束运行机器人的函数

        .. seealso::
            更多教程和相关资讯可参阅：
            https://qg-botsdk.readthedocs.io/zh_CN/latest/index.html
        """
        if self.__running:
            self.__await_closure = True
            self.__running = False
            self.logger.info("WS链接已开始结束进程，请等待另一端完成握手并等待 TCP 连接终止")
            self._bot_class.running = False
            self._loop.create_task(self._bot_class.close())
        else:
            self.logger.error("当前机器人没有运行！")
