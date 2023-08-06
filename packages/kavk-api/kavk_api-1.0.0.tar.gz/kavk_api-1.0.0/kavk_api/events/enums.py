'''
Большинство enum взято из https://github.com/python273/vk_api/
Автор: python273
'''
from enum import IntEnum, Enum

CHAT_START_ID = int(2E9)  # id с которого начинаются беседы

class VkEventType(IntEnum):
    REPLACE_MESSAGE_FLAGS = 1
    SET_MESSAGE_FLAGS = 2
    RESET_MESSAGE_FLAGS = 3
    MESSAGE_NEW = 4
    MESSAGE_EDIT = 5
    READ_INCOMING_MESSAGES = 6
    READ_OUTGOING_MESSAGES = 7
    FRIEND_ONLINE = 8
    FRIEND_OFFLINE = 9
    RESET_DIALOG_FLAGS = 10
    REPLACE_DIALOG_FLAGS = 11
    SET_DIALOG_FLAGS = 12
    DELETE_DIALOG_MESSAGES = 13
    RESTORE_DIALOG_MESSAGES = 14
    CHANGE_MAJOR_ID = 20
    CHANGE_MINOR_ID = 21
    CHAT_SETTINGS_CHANGE = 51
    CHAT_INFO_CHANGED = 52
    USER_TYPING_IN_DIALOG = 61
    USER_TYPING_IN_CHAT = 62
    USERS_TYPING_IN_CHAT = 63
    USER_VOICE_RECORDING = 64
    USER_UPLOAD_PHOTO = 65
    USER_UPLOAD_VIDEO = 66
    USER_UPLOAD_FILE = 67
    USER_CALL = 115
    CHANGE_COUNT_OF_UNREAD_DIALOGS = 80
    CHANGE_INVISIBLE = 81
    FRIEND_STATE_CHANGE = 90
    NOTIFICATION_CHANGE = 114
    MESSAGE_REACTION_NEW = 601


class BotEventType(Enum):
    MESSAGE_NEW = 'message_new'
    MESSAGE_REPLY = 'message_reply'
    MESSAGE_EDIT = 'message_edit'
    MESSAGE_ALLOW = 'message_allow'
    MESSAGE_DENY = 'message_deny'
    MESSAGE_TYPING_STATE = 'message_typing_state'
    MESSAGE_EVENT = 'message_event'

    PHOTO_NEW = 'photo_new'
    PHOTO_COMMENT_NEW = 'photo_comment_new'
    PHOTO_COMMENT_EDIT = 'photo_comment_edit'
    PHOTO_COMMENT_RESTORE = 'photo_comment_restore'

    AUDIO_NEW = 'audio_new'

    VIDEO_NEW = 'video_new'
    VIDEO_COMMENT_NEW = 'video_comment_new'
    VIDEO_COMMENT_EDIT = 'video_comment_edit'
    VIDEO_COMMENT_RESTORE = 'video_comment_restore'
    VIDEO_COMMENT_DELETE = 'video_comment_delete'

    WALL_POST_NEW = 'wall_post_new'
    WALL_REPOST = 'wall_repost'
    WALL_REPLY_NEW = 'wall_reply_new'
    WALL_REPLY_EDIT = 'wall_reply_edit'
    WALL_REPLY_RESTORE = 'wall_reply_restore'
    WALL_REPLY_DELETE = 'wall_reply_delete'

    LIKE_ADD = 'like_add'
    LIKE_REMOVE = 'like_remove'

    BOARD_POST_NEW = 'board_post_new'
    BOARD_POST_EDIT = 'board_post_edit'
    BOARD_POST_RESTORE = 'board_post_restore'
    BOARD_POST_DELETE = 'board_post_delete'

    MARKET_COMMENT_NEW = 'market_comment_new'
    MARKET_COMMENT_EDIT = 'market_comment_edit'
    MARKET_COMMENT_RESTORE = 'market_comment_restore'
    MARKET_COMMENT_DELETE = 'market_comment_delete'
    MARKET_ORDER_NEW = 'marker_order_new'
    MARKET_ORDER_EDIT = 'marker_order_edit'

    GROUP_LEAVE = 'group_leave'
    GROUP_JOIN = 'group_join'
    USER_BLOCK = 'user_block'

    USER_UNBLOCK = 'user_unblock'

    POLL_VOTE_NEW = 'poll_vote_new'
    GROUP_OFFICERS_EDIT = 'group_officers_edit'
    GROUP_CHANGE_SETTINGS = 'group_change_settings'
    GROUP_CHANGE_PHOTO = 'group_change_photo'
    VKPAY_TRANSACTION = 'vkpay_transaction'
    APP_PAYLOAD = 'app_payload'

    DONUT_SUBSCRIPTION_CREATE = 'donut_subscription_create'
    DONUT_SUBSCRIPTION_EXPIRED = 'donut_subscription_expired'
    DONUT_SUBSCRIPTION_CANCELLED = 'donut_subscription_cancelled'
    DONUT_SUBSCRIPTION_PRICE_CHANGED = 'donut_subscription_price_changed'
    DONUT_MONEY_WITHDRAW = 'donut_money_withdraw'
    DONUT_MONEY_WITHDRAW_ERROR = 'donut_money_withdraw_error'


class VkLongpollMode(IntEnum):
    """ Дополнительные опции ответа
    `Подробнее в документации VK API
    <https://vk.com/dev/using_longpoll?f=1.+Подключение>`_
    """

    #: Получать вложения
    GET_ATTACHMENTS = 2

    #: Возвращать расширенный набор событий
    GET_EXTENDED = 2**3

    #: возвращать pts для метода `messages.getLongPollHistory`
    GET_PTS = 2**5

    #: В событии с кодом 8 (друг стал онлайн) возвращать
    #: дополнительные данные в поле `extra`
    GET_EXTRA_ONLINE = 2**6

    #: Возвращать поле `random_id`
    GET_RANDOM_ID = 2**7


DEFAULT_MODE = sum(VkLongpollMode)


class VkPlatform(IntEnum):
    """ Идентификаторы платформ """

    #: Мобильная версия сайта или неопознанное мобильное приложение
    MOBILE = 1

    #: Официальное приложение для iPhone
    IPHONE = 2

    #: Официальное приложение для iPad
    IPAD = 3

    #: Официальное приложение для Android
    ANDROID = 4

    #: Официальное приложение для Windows Phone
    WPHONE = 5

    #: Официальное приложение для Windows 8
    WINDOWS = 6

    #: Полная версия сайта или неопознанное приложение
    WEB = 7


class VkOfflineType(IntEnum):
    """ Выход из сети в событии :attr:`VkEventType.USER_OFFLINE` """

    #: Пользователь покинул сайт
    EXIT = 0

    #: Оффлайн по таймауту
    AWAY = 1


class VkMessageFlag(IntEnum):
    """ Флаги сообщений """

    #: Сообщение не прочитано.
    UNREAD = 1

    #: Исходящее сообщение.
    OUTBOX = 2

    #: На сообщение был создан ответ.
    REPLIED = 2**2

    #: Помеченное сообщение.
    IMPORTANT = 2**3

    #: Сообщение отправлено через чат.
    CHAT = 2**4

    #: Сообщение отправлено другом.
    #: Не применяется для сообщений из групповых бесед.
    FRIENDS = 2**5

    #: Сообщение помечено как "Спам".
    SPAM = 2**6

    #: Сообщение удалено (в корзине).
    DELETED = 2**7

    #: Сообщение проверено пользователем на спам.
    FIXED = 2**8

    #: Сообщение содержит медиаконтент
    MEDIA = 2**9

    #: Приветственное сообщение от сообщества.
    HIDDEN = 2**16

    #: Сообщение удалено для всех получателей.
    DELETED_ALL = 2**17


class VkPeerFlag(IntEnum):
    """ Флаги диалогов """

    #: Важный диалог
    IMPORTANT = 1

    #: Неотвеченный диалог
    UNANSWERED = 2


class VkChatEventType(IntEnum):
    """ Идентификатор типа изменения в чате """

    #: Изменилось название беседы
    TITLE = 1

    #: Сменилась обложка беседы
    PHOTO = 2

    #: Назначен новый администратор
    ADMIN_ADDED = 3

    #: Изменены настройки беседы
    SETTINGS_CHANGED = 4

    #: Закреплено сообщение
    MESSAGE_PINNED = 5

    #: Пользователь присоединился к беседе
    USER_JOINED = 6

    #: Пользователь покинул беседу
    USER_LEFT = 7

    #: Пользователя исключили из беседы
    USER_KICKED = 8

    #: С пользователя сняты права администратора
    ADMIN_REMOVED = 9

    #: Бот прислал клавиатуру
    KEYBOARD_RECEIVED = 11


