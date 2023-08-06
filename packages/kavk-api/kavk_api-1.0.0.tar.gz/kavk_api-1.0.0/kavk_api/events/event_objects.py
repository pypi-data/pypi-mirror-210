from typing import Optional
from pydantic import BaseModel as BM
from ..api.objects import (AudioAudio, BoardTopicComment, MarketOrder, MessagesMessage, PhotosPhoto, 
                      VideoVideo, WallWallComment, WallWallpostFull)

# Все значения поля object ивентов из ссылки ниже
# https://dev.vk.com/api/community-events/json-schema 

class ClientInfo(BM):
    button_actions:list[str]
    keyboard:bool
    inline_keyboard:bool
    carousel:bool
    lang_id:int

class MessageNewObject(BM):
    message:MessagesMessage
    client_info:ClientInfo

class MessageReplyObject(MessagesMessage): pass

class MessageEditObject(MessagesMessage):pass

class MessageAllowObject(BM):
    user_id:int
    key:str

class MessageDenyObject(BM):
    user_id:int

class MessageTypingStateObject(BM):
    state:str
    from_id:int
    to_id:int

class MessageEventObject(BM):
    user_id:int
    peer_id:int
    event_id:str
    payload:str
    conversation_message_id:int
    
class PhotoNewObject(PhotosPhoto): pass

class PhotoObject(BM):
    photo_id:int
    photo_owner_id:int

class AudioNewObject(AudioAudio): pass

class VideoNewObject(VideoVideo): pass

class VideoCommentObject(BM):
    video_id:int
    video_owner_id:int

class VideoCommentDeleteObject(BM):
    owner_id:int
    id:int
    user_id:int
    deleter_id:int
    video_id:int

class WallObject(WallWallpostFull):
    postponed_id:Optional[int] = None

class WallReplyObject(WallWallComment):
    post_id:int
    post_owner_id:int

class WallReplyDeleteObject(BM):
    owner_id:int
    id:int
    deleter_id:int
    post_id:int


class LikeObject(BM):
    liker_id:int
    object_type:str
    object_owner_id:int
    object_id:int
    thread_reply_id:Optional[int]
    post_id:int


class BoardPostObject(BoardTopicComment):
    topic_id:int
    topic_owner_id:int

class BoardPostDeleteObject(BM):
    id:int
    topic_id:int
    topic_owner_id:int


class MarketCommentObject(WallWallComment):
    market_owner_id:int
    item_id:int

class MarketCommentDeleteObject(BM):
    owner_id:int
    id:int
    user_id:int
    deleter_id:int
    item_id:int

class MarketOrderObject(MarketOrder): pass


class GroupLeaveObject(BM):
    user_id:int
    self:int

class GroupJoinObject(BM):
    user_id:int
    join_type:str

class UserBlockObject(BM):
    admin_id:int
    user_id:int
    unblock_date:int
    reason:int
    comment:str # Приходит всегда

class UserUnblockObject(BM):
    admin_id:int
    user_id:int
    by_end_date:int


class PollVoteNewObject(BM):
    owner_id:int
    poll_id:int
    option_id:int
    user_id:int

class GroupOfficersEditObject(BM):
    admin_id:int
    user_id:int
    level_old:int
    level_new:int

class GroupChangeSettingsObject(BM):
    user_id:int
    changes:dict[str,str] # Мне лень эту хуйню делать + она никому наверняка нахуй не сдалась

class GroupChangePhotoObject(BM):
    user_id:int
    photo:PhotosPhoto

class VkPayTransactionObject(BM): # Нврн не правильно, но я хз как тестить
    from_id:int
    amount:int
    description:str
    date:int

class AppPayloadObject(BM):
    user_id:int
    app_id:int
    payload:str # Нврн не правильный тип
    group_id:int


class DonutSubscriptionCreateObject(BM):
    amount:int
    amount_without_fee:float
    user_id:int

class DonutSubscriptionProlongedObject(DonutSubscriptionCreateObject): pass

class DonutSubscriptionExpiredObject(BM):
    user_id:int

class DonutSubscriptionCancelledObject(BM):
    user_id:int

class DonutSubscriptionPriceChangedObject(BM):
    amount_old:int
    amount_new:int
    amount_diff:float
    amount_diff_without_fee:float
    user_id:int

class DonutMoneyWithdrawObject(BM):
    amount:float
    amount_without_fee:float

class DonutMoneyWithdrawErrorObject(BM):
    reason:str


__all__ = (
        "ClientInfo", "MessageNewObject", "MessageReplyObject",
        "MessageEditObject", "MessageAllowObject", "MessageDenyObject",
        "MessageTypingStateObject", "MessageEventObject", "PhotoNewObject",
        "PhotoObject", "AudioNewObject", "VideoNewObject",
        "VideoCommentObject", "VideoCommentDeleteObject", "WallObject","WallReplyObject",
        "WallReplyDeleteObject", "LikeObject", "BoardPostObject",
        "BoardPostDeleteObject", "MarketCommentObject", "MarketCommentDeleteObject",
        "MarketOrderObject", "GroupLeaveObject", "GroupJoinObject",
        "UserBlockObject", "UserUnblockObject", "PollVoteNewObject",
        "GroupOfficersEditObject", "GroupChangeSettingsObject", "GroupChangePhotoObject",
        "VkPayTransactionObject", "AppPayloadObject", "DonutSubscriptionCreateObject",
        "DonutSubscriptionProlongedObject", "DonutSubscriptionExpiredObject", "DonutSubscriptionCancelledObject",
        "DonutSubscriptionPriceChangedObject", "DonutMoneyWithdrawObject", "DonutMoneyWithdrawErrorObject"
        )
