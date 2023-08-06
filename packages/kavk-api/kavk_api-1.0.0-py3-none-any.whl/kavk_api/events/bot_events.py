from typing import Union, Any
from pydantic import BaseModel as BM
from .enums import BotEventType as BET
from .enums import CHAT_START_ID
from .event_objects import *

class EventWrongException(Exception):
    pass

class BaseEvent(BM):
    raw:dict
    group_id:int
    v:str
    object:Any # ЗАГЛУШКА

    @property
    def type(self):
        return type(self)

class MessageNew(BaseEvent):
    object:MessageNewObject
    from_chat:bool = False
    from_user:bool = False
    from_group:bool = False
    chat_id:int|None = None

    def __init__(self, **data):
        super().__init__(**data)

        peer_id = self.object.message.peer_id
        if peer_id < 0:
            self.from_group = True
        elif peer_id > CHAT_START_ID:
            self.from_chat = True
        else: self.from_user = True

        if self.from_chat:
            self.chat_id = peer_id - CHAT_START_ID



class MessageReply(BaseEvent):
    object:MessageReplyObject

class MessageEdit(BaseEvent):
    object:MessageEditObject

class MessageAllow(BaseEvent):
    object:MessageAllowObject

class MessageDeny(BaseEvent):
    object:MessageDenyObject

class MessageTypingState(BaseEvent):
    object:MessageTypingStateObject

class MessageEvent(BaseEvent):
    object:MessageEventObject


class PhotoNew(BaseEvent):
    object:PhotoNewObject

class PhotoCommentNew(BaseEvent):
    object:PhotoObject

class PhotoCommentEdit(BaseEvent):
    object:PhotoObject

class PhotoCommentRestore(BaseEvent):
    object:PhotoObject


class AudioNew(BaseEvent):
    object:AudioNewObject


class VideoNew(BaseEvent):
    object:VideoNewObject

class VideoCommentNew(BaseEvent):
    object:VideoCommentObject

class VideoCommentEdit(BaseEvent):
    object:VideoCommentObject

class VideoCommentRestore(BaseEvent):
    object:VideoCommentObject

class VideoCommentDelete(BaseEvent):
    object:VideoCommentDeleteObject


class WallPostNew(BaseEvent):
    object:WallObject

class WallRepost(BaseEvent):
    object:WallObject


class WallReplyNew(BaseEvent):
    object:WallReplyObject

class WallReplyEdit(BaseEvent):
    object:WallReplyObject

class WallReplyRestore(BaseEvent):
    object:WallReplyObject

class WallReplyDelete(BaseEvent):
    object:WallReplyDeleteObject


class LikeAdd(BaseEvent):
    object:LikeObject

class LikeRemove(BaseEvent):
    object:LikeObject


class BoardPostNew(BaseEvent):
    object:BoardPostObject

class BoardPostEdit(BaseEvent):
    object:BoardPostObject

class BoardPostRestore(BaseEvent):
    object:BoardPostObject

class BoardPostDelete(BaseEvent):
    object:BoardPostDeleteObject


class MarketCommentNew(BaseEvent):
    object:MarketCommentObject

class MarketCommentEdit(BaseEvent):
    object:MarketCommentObject

class MarketCommentRestore(BaseEvent):
    object:MarketCommentObject

class MarketCommentDelete(BaseEvent):
    object:MarketCommentDeleteObject

class MarketOrderNew(BaseEvent):
    object:MarketOrderObject

class MarketOrderEdit(BaseEvent):
    object:MarketOrderObject


class GroupJoin(BaseEvent):
    object:GroupJoinObject

class GroupLeave(BaseEvent):
    object:GroupLeaveObject

class UserBlock(BaseEvent):
    object:UserBlockObject

class UserUnblock(BaseEvent):
    object:UserUnblockObject


class PollVoteNew(BaseEvent):
    object:PollVoteNewObject

class GroupOfficersEdit(BaseEvent):
    object:GroupOfficersEditObject

class GroupChangeSettings(BaseEvent):
    object:GroupChangeSettingsObject

class GroupChangePhoto(BaseEvent):
    object:GroupChangePhotoObject

class VkPayTransaction(BaseEvent):
    object:VkPayTransactionObject

class AppPayload(BaseEvent):
    object:AppPayloadObject


class DonutSubscriptionCreate(BaseEvent):
    object:DonutSubscriptionCreateObject

class DonutSubscriptionProlonged(BaseEvent):
    object:DonutSubscriptionProlongedObject

class DonutSubscriptionExpired(BaseEvent):
    object:DonutSubscriptionExpiredObject

class DonutSubscriptionCancelled(BaseEvent):
    object:DonutSubscriptionCancelledObject

class DonutSubscriptionPriceChanged(BaseEvent):
    object:DonutSubscriptionPriceChangedObject

class DonutMoneyWithdraw(BaseEvent):
    object:DonutMoneyWithdrawObject

class DonutMoneyWithdrawError(BaseEvent):
    object:DonutMoneyWithdrawErrorObject

AnyBotEvent = Union[MessageNew, MessageReply, MessageEdit, MessageAllow, MessageDeny, MessageTypingState, MessageEvent, PhotoNew, PhotoCommentNew, PhotoCommentEdit, PhotoCommentRestore, AudioNew, VideoNew, VideoCommentNew, VideoCommentEdit, VideoCommentRestore, VideoCommentDelete, WallPostNew, WallRepost, WallReplyNew, WallReplyEdit, WallReplyRestore, WallReplyDelete, LikeAdd, LikeRemove, BoardPostNew, BoardPostEdit, BoardPostRestore, BoardPostDelete, MarketCommentNew, MarketCommentEdit, MarketCommentRestore, MarketCommentDelete, MarketOrderNew, MarketOrderEdit, GroupJoin, GroupLeave, UserBlock, UserUnblock, PollVoteNew, GroupOfficersEdit, GroupChangeSettings, GroupChangePhoto, VkPayTransaction, AppPayload, DonutSubscriptionCreate, DonutSubscriptionProlonged, DonutSubscriptionExpired, DonutSubscriptionCancelled, DonutSubscriptionPriceChanged, DonutMoneyWithdraw, DonutMoneyWithdrawError]

def _get_event(event_type:str):
    event = BET(event_type)
    match event:
        case BET.MESSAGE_NEW: r = MessageNew
        case BET.MESSAGE_NEW: r = MessageNew
        case BET.MESSAGE_EDIT: r = MessageEdit
        case BET.MESSAGE_DENY: r = MessageDeny
        case BET.MESSAGE_REPLY: r = MessageReply
        case BET.MESSAGE_ALLOW: r = MessageAllow
        case BET.MESSAGE_TYPING_STATE: r = MessageTypingState
        case BET.MESSAGE_EVENT: r = MessageEvent
        case BET.PHOTO_NEW: r = PhotoNew
        case BET.PHOTO_COMMENT_NEW: r = PhotoCommentNew
        case BET.PHOTO_COMMENT_EDIT: r = PhotoCommentEdit
        case BET.PHOTO_COMMENT_RESTORE: r = PhotoCommentRestore
        case BET.AUDIO_NEW: r = AudioNew
        case BET.VIDEO_COMMENT_NEW: r = VideoCommentNew
        case BET.VIDEO_COMMENT_EDIT: r = VideoCommentEdit
        case BET.VIDEO_COMMENT_RESTORE: r = VideoCommentRestore
        case BET.VIDEO_COMMENT_DELETE: r = VideoCommentDelete
        case BET.WALL_POST_NEW: r = WallPostNew
        case BET.WALL_REPOST: r = WallRepost
        case BET.WALL_REPLY_NEW: r = WallReplyNew
        case BET.WALL_REPLY_EDIT: r = WallReplyEdit
        case BET.WALL_REPLY_RESTORE: r = WallReplyRestore
        case BET.WALL_REPLY_DELETE: r = WallReplyDelete
        case BET.LIKE_ADD: r = LikeAdd
        case BET.LIKE_REMOVE: r = LikeRemove
        case BET.BOARD_POST_NEW: r = BoardPostNew
        case BET.BOARD_POST_EDIT: r = BoardPostEdit
        case BET.BOARD_POST_RESTORE: r = BoardPostRestore
        case BET.BOARD_POST_DELETE: r = BoardPostDelete
        case BET.MARKET_COMMENT_NEW: r = MarketCommentNew
        case BET.MARKET_COMMENT_EDIT: r = MarketCommentEdit
        case BET.MARKET_COMMENT_RESTORE: r = MarketCommentRestore
        case BET.MARKET_COMMENT_DELETE: r = MarketCommentDelete
        case BET.MARKET_ORDER_NEW: r = MarketOrderNew
        case BET.MARKET_ORDER_EDIT: r = MarketOrderEdit
        case BET.GROUP_LEAVE: r = GroupLeave
        case BET.GROUP_JOIN: r = GroupJoin
        case BET.USER_BLOCK: r = UserBlock
        case BET.USER_UNBLOCK: r =  UserUnblock
        case BET.POLL_VOTE_NEW: r = PollVoteNew
        case BET.GROUP_OFFICERS_EDIT: r = GroupOfficersEdit
        case BET.GROUP_CHANGE_SETTINGS: r = GroupChangeSettings
        case BET.GROUP_CHANGE_PHOTO: r = GroupChangePhoto
        case BET.VKPAY_TRANSACTION: r = VkPayTransaction
        case BET.APP_PAYLOAD: r = AppPayload
        case BET.DONUT_SUBSCRIPTION_CREATE: r = DonutSubscriptionCreate
        case BET.DONUT_SUBSCRIPTION_EXPIRED: r = DonutSubscriptionExpired
        case BET.DONUT_SUBSCRIPTION_CANCELLED: r = DonutSubscriptionCancelled
        case BET.DONUT_SUBSCRIPTION_PRICE_CHANGED: r = DonutSubscriptionPriceChanged
        case BET.DONUT_MONEY_WITHDRAW: r = DonutMoneyWithdraw
        case BET.DONUT_MONEY_WITHDRAW_ERROR: r = DonutMoneyWithdrawError
        case _: raise EventWrongException(event, 'not found! Please, make issue on github.com/kravandir/kavk_api')
    return r


__all__ = (
"MessageNew","MessageReply","MessageEdit","MessageAllow","MessageDeny","MessageTypingState","MessageEvent","PhotoNew",
"PhotoCommentNew","PhotoCommentEdit","PhotoCommentRestore","AudioNew","VideoNew","VideoCommentNew","VideoCommentEdit",
"VideoCommentRestore","VideoCommentDelete","WallPostNew","WallRepost","WallReplyNew","WallReplyEdit",
"WallReplyRestore","WallReplyDelete","LikeAdd","LikeRemove","BoardPostNew","BoardPostEdit",
"BoardPostRestore","BoardPostDelete","MarketCommentNew","MarketCommentEdit","MarketCommentRestore",
"MarketCommentDelete","MarketOrderNew","MarketOrderEdit","GroupJoin","GroupLeave", "UserBlock","UserUnblock",
"PollVoteNew", "GroupOfficersEdit", "GroupChangeSettings", "GroupChangePhoto", "VkPayTransaction", "AppPayload",
"DonutSubscriptionCreate", "DonutSubscriptionProlonged", "DonutSubscriptionExpired","DonutSubscriptionCancelled",
"DonutSubscriptionPriceChanged", "DonutMoneyWithdraw", "DonutMoneyWithdrawError", "_get_event", 'EventWrongException', 'AnyBotEvent'
)
