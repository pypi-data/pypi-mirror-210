from pydantic import BaseModel
from pydantic.fields import ModelField
from typing import Optional, Any, Union
from .enums import VkMessageFlag, VkEventType
from ..api.objects import MessagesKeyboard

class WrongTypeException(Exception): pass

class Additional(BaseModel):
    title:str = '...'
    emoji:bool = False
    from_:int = 0
    has_template:bool = False
    marked_users:Optional[list[list]] = None
    keyboard:Optional[MessagesKeyboard] = None
    expire_ttl:Optional[int] = None
    ttl:Optional[int] = None
    is_expired:Optional[bool] = None
    payload:Optional[str] = None

class Attachments(BaseModel):
    fwd:str = '0_0'
    reply:Optional[dict|str] = None
    attach_count:int = 0
    attach1:Optional[str] = None
    attach1:Optional[str] = None
    attach1_type:Optional[str] = None
    attach2:Optional[str] = None
    attach2_type:Optional[str] = None
    attach3:Optional[str] = None
    attach3_type:Optional[str] = None
    attach4:Optional[str] = None
    attach4_type:Optional[str] = None
    attach5:Optional[str] = None
    attach5_type:Optional[str] = None
    attach6:Optional[str] = None
    attach6_type:Optional[str] = None
    attach7:Optional[str] = None
    attach7_type:Optional[str] = None
    attach8:Optional[str] = None
    attach8_type:Optional[str] = None
    attach9:Optional[str] = None
    attach9_type:Optional[str] = None
    attach10:Optional[str] = None
    attach10_type:Optional[str] = None

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        for i in range(1,11):
            name = 'attach'+str(i) # Получаем допустим attach{i}
            if data.get(name) != None: # Если attach{i} есть в data увеличиваем счетчик
                self.attach_count += 1 
            else: break # Если нет, то и других не будет, кончаем дело


class BaseEvent(BaseModel):
    from_user:bool = False
    from_chat:bool = False
    from_group:bool = False
    from_me:bool = False
    to_me:bool = False
    raw:list = []
    type:VkEventType

    def __init__(self, **data) -> None:
        type = self.__class__.__dict__.get('__fields__',{}).get('type')
        try: 
            data_type = VkEventType(data.get('type'))
        except: raise WrongTypeException('type {} not found in EventsType!'.format(data.get('type')))
        if isinstance(type, ModelField):
            if not isinstance(type.default, VkEventType):
                raise WrongTypeException('{} class doesn\'t have default type!'.format(self.__class__.__name__))
            elif type.default != data_type:
                raise WrongTypeException('{} class doesn\'t support {} type'.format(self.__class__.__name__, data.get('type')))
        else: raise WrongTypeException('{} class doesn\'t have default type!'.format(self.__class__.__name__))
        if isinstance(data.get('message', None), str):
            data.update({'message': data['message'].replace('&lt;', '<') \
            .replace('&gt;', '>') \
            .replace('&quot;', '"') \
            .replace('&amp;', '&') \
            .replace('<br>', '\n')
                         })

        super().__init__(**data)
        if hasattr(self, 'user_id'):
            if self.user_id < 0 and isinstance(self.user_id, int):
                self.user_id = -self.user_id

        for i in ('from_', 'peer_id'):
            if data.get(i) != None:
                if data[i] < 0:
                    self.from_group = True
                elif data[i] > int(2E9):
                    self.from_chat = True
                else: 
                    self.from_user = True
                if data.get('flags', 0) & VkMessageFlag.OUTBOX:
                    self.from_me = True
                else: self.to_me = True
        if data.get('chat_id') != None: self.from_chat = True
        if data.get('user_id') != None: self.from_user = True

    
    @classmethod
    def from_list(cls, values:list):
        d = {'raw': values.copy()}
        keys = list(cls.__dict__['__fields__'].keys())[6:] # Пропускаем from_... и начинаем с type
        for key, value in zip(keys, values):
            d.update({key:value})
        return cls(**d)


class ReplaceMessageFlags(BaseEvent):
    type = VkEventType.REPLACE_MESSAGE_FLAGS
    flags:int

class SetMessageFlags(BaseEvent):
    type = VkEventType.SET_MESSAGE_FLAGS
    message_id:int
    mask:int

class ResetMessageFlags(BaseEvent):
    type = VkEventType.RESET_MESSAGE_FLAGS
    message_id:int
    mask:int

class MessageNew(BaseEvent):
    type = VkEventType.MESSAGE_NEW
    message_id:int = 0
    flags:int = 0
    peer_id:int
    timestamp:int = 0
    message:str = ''
    additional:Additional = Additional()
    attachments:Attachments = Attachments()
    random_id:int = 0

class MessageEdit(BaseEvent):
    type = VkEventType.MESSAGE_EDIT
    message_id:int
    mask:int
    peer_id:int
    timestamp:int = 0
    new_text:str
    additional:Additional = Additional()
    attachments:Attachments = Attachments()

class ReadIncomingMessages(BaseEvent):
    type = VkEventType.READ_INCOMING_MESSAGES
    peer_id:int
    message_id:int
    local_id:int

class ReadOutgoingMessages(BaseEvent):
    type = VkEventType.READ_OUTGOING_MESSAGES
    peer_id:int
    message_id:int
    local_id:int

class FriendOnline(BaseEvent):
    type = VkEventType.FRIEND_ONLINE
    user_id:int = 0
    platform:int = 0
    timestamp:int = 0
    app_id:int = 0
    is_mobile:int = 0
    has_invisible_mod:int = 0

class FriendOffline(BaseEvent):
    type = VkEventType.FRIEND_OFFLINE
    user_id:int
    flags:int
    timestamp:int

class ResetDialogFlags(BaseEvent):
    type = VkEventType.RESET_DIALOG_FLAGS
    peer_id:int
    flags:int

class ReplaceDialogFlags(BaseEvent):
    type = VkEventType.REPLACE_DIALOG_FLAGS
    peer_id:int
    flags:int

class SetDialogFlags(BaseEvent):
    type = VkEventType.SET_DIALOG_FLAGS
    peer_id:int
    flags:int

class DeleteDialogMessages(BaseEvent):
    type = VkEventType.DELETE_DIALOG_MESSAGES
    peer_id:int
    local_id:int

class RestoreDialogMessages(BaseEvent):
    type = VkEventType.RESTORE_DIALOG_MESSAGES
    peer_id:int
    local_id:int

class ChangeMajorId(BaseEvent):
    type = VkEventType.CHANGE_MAJOR_ID
    peer_id:int
    major_id:int

class ChangeMinorId(BaseEvent):
    type = VkEventType.CHANGE_MINOR_ID
    peer_id:int
    minor_id:int

class ChatSettingsChange(BaseEvent):
    type = VkEventType.CHAT_SETTINGS_CHANGE
    chat_id:int
    self_:Optional[int]

class ChatInfoChanged(BaseEvent):
    type = VkEventType.CHAT_INFO_CHANGED
    type_id:int
    peer_id:int 
    info:int|str

class UserTypingInDialog(BaseEvent):
    type = VkEventType.USER_TYPING_IN_DIALOG
    user_id:int
    flags:int = 1

class UserTypingInChat(BaseEvent):
    type = VkEventType.USER_TYPING_IN_CHAT
    user_id:int
    chat_id:int

class UsersTypingInChat(BaseEvent):
    type = VkEventType.USERS_TYPING_IN_CHAT
    peer_id:int
    user_ids:list[int]
    total_count:int
    timestamp:int = 0

class UserVoiceRecording(UsersTypingInChat): # Один и тот же буквально как и следующие
    type = VkEventType.USER_VOICE_RECORDING

class UserUploadPhoto(UsersTypingInChat):
    type = VkEventType.USER_UPLOAD_PHOTO

class UserUploadVideo(UsersTypingInChat):
    type = VkEventType.USER_UPLOAD_VIDEO

class UserUploadFile(UsersTypingInChat):
    type = VkEventType.USER_UPLOAD_PHOTO

class UserCall(BaseEvent):
    type = VkEventType.USER_CALL
    user_id:int
    call_id:int

class ChangeCountOfUnreadDialogs(BaseEvent):
    type = VkEventType.CHANGE_COUNT_OF_UNREAD_DIALOGS
    unread_count:Optional[int]
    unread_unmuted_count:Optional[int]
    show_only_unmuted:Optional[bool]
    business_notify_unread_count:Optional[int]
    header_unread_count:Optional[int]
    header_unread_unmuted_count:Optional[int]
    archive_unread_count:Optional[int]
    archive_unread_unmuted_count:Optional[int]
    archive_mentions_count:Optional[int]

class ChangeInvisible(BaseEvent):
    type = VkEventType.CHANGE_INVISIBLE
    user_id:int
    state:int = 0
    timestamp:int = 0

class FriendStateChange(BaseEvent):
    type = VkEventType.FRIEND_STATE_CHANGE
    state:int
    user_id:int

class NotificationChange(BaseEvent):
    type = VkEventType.FRIEND_STATE_CHANGE
    peer_id:int
    sound:int
    disabled_until:int

class MessageReactionNew(BaseEvent):
    type = VkEventType.MESSAGE_REACTION_NEW
    

def _get_event(raw:list) -> Union[ReplaceMessageFlags, SetMessageFlags, ResetMessageFlags, MessageNew, MessageEdit, ReadIncomingMessages, ReadOutgoingMessages, FriendOnline, FriendOffline, ResetDialogFlags, ReplaceDialogFlags, SetDialogFlags, DeleteDialogMessages, RestoreDialogMessages, ChangeMajorId, ChangeMinorId, ChatSettingsChange, ChatInfoChanged, UserTypingInDialog, UserTypingInChat, UsersTypingInChat, UserVoiceRecording, UserUploadPhoto, UserUploadVideo, UserUploadFile, UserCall, ChangeCountOfUnreadDialogs, ChangeInvisible, FriendStateChange, NotificationChange]:
    for e in EVENTS:
        try:
            return e.from_list(raw)
        except: pass

    raise WrongTypeException('Wrong event! {}\nPlease report this event at github.com/kravandir/kavk_api/issues'.format(raw))


EVENTS = [ReplaceMessageFlags, SetMessageFlags, ResetMessageFlags, MessageNew, MessageEdit, ReadIncomingMessages, ReadOutgoingMessages, FriendOnline, FriendOffline, ResetDialogFlags, ReplaceDialogFlags, SetDialogFlags, DeleteDialogMessages, RestoreDialogMessages, ChangeMajorId, ChangeMinorId, ChatSettingsChange, ChatInfoChanged, UserTypingInDialog, UserTypingInChat, UsersTypingInChat, UserVoiceRecording, UserUploadPhoto, UserUploadVideo, UserUploadFile, UserCall, ChangeCountOfUnreadDialogs, ChangeInvisible, FriendStateChange, NotificationChange]
