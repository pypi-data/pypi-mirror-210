from typing import Optional
from .objects import *
from .base import BL, BM, Int, Bool, Str

class AccountChangePasswordResponse(BM):
	token:str
	secret:Optional[str] = None

class AccountGetActiveOffersResponse(BM):
	count:int
	items:list["AccountOffer"]

class AccountGetAppPermissionsResponse(Int): pass

class AccountGetBannedResponse(BM):
	count:int
	items:list[int]
	profiles:Optional[list["UsersUserFull"]] = None
	groups:Optional[list["GroupsGroup"]] = None

class AccountGetCountersResponse(AccountAccountCounters): pass

class AccountGetInfoResponse(AccountInfo): pass

class AccountGetProfileInfoResponse(AccountUserSettings): pass

class AccountGetPushSettingsResponse(AccountPushSettings): pass

class AccountSaveProfileInfoResponse(BM):
	changed:bool
	name_request:Optional[AccountNameRequest] = None


class AdsAddOfficeUsersResponse(Bool): pass

class AdsCheckLinkResponse(AdsLinkStatus): pass

class AdsCreateAdsResponse(BL):
	__root__:list["AdsCreateAdStatus"]

class AdsCreateCampaignsResponse(BL):
	__root__:list["AdsCreateCampaignStatus"]

class AdsCreateClientsResponse(BL):
	__root__:list[int]

class AdsCreateTargetGroupResponse(BM):
	id:Optional[int] = None
	pixel:Optional[str] = None

class AdsDeleteAdsResponse(BL):
	__root__:list[int]

class AdsDeleteCampaignsResponse(BL):
	__root__:list[int]

class AdsDeleteClientsResponse(BL):
	__root__:list[int]

class AdsGetAccountsResponse(BL):
	__root__:list["AdsAccount"]

class AdsGetAdsLayoutResponse(BL):
	__root__:list["AdsAdLayout"]

class AdsGetAdsTargetingResponse(BL):
	__root__:list["AdsTargSettings"]

class AdsGetAdsResponse(BL):
	__root__:list["AdsAd"]

class AdsGetBudgetResponse(Int): pass

class AdsGetCampaignsResponse(BL):
	__root__:list["AdsCampaign"]

class AdsGetCategoriesResponse(BM):
	v1:Optional[list["AdsCategory"]] = None
	v2:Optional[list["AdsCategory"]] = None

class AdsGetClientsResponse(BL):
	__root__:list["AdsClient"]

class AdsGetDemographicsResponse(BL):
	__root__:list["AdsDemoStats"]

class AdsGetFloodStatsResponse(AdsFloodStats): pass

class AdsGetLookalikeRequestsResponse(BM):
	count:int
	items:list["AdsLookalikeRequest"]

class AdsGetMusiciansResponse(BM):
	items:list["AdsMusician"]

class AdsGetOfficeUsersResponse(BL):
	__root__:list["AdsUsers"]

class AdsGetPostsReachResponse(BL):
	__root__:list["AdsPromotedPostReach"]

class AdsGetRejectionReasonResponse(AdsRejectReason): pass

class AdsGetStatisticsResponse(BL):
	__root__:list["AdsStats"]

class AdsGetSuggestionsCitiesResponse(BL):
	__root__:list["AdsTargSuggestionsCities"]

class AdsGetSuggestionsRegionsResponse(BL):
	__root__:list["AdsTargSuggestionsRegions"]

class AdsGetSuggestionsResponse(BL):
	__root__:list["AdsTargSuggestions"]

class AdsGetSuggestionsSchoolsResponse(BL):
	__root__:list["AdsTargSuggestionsSchools"]

class AdsGetTargetGroupsResponse(BL):
	__root__:list["AdsTargetGroup"]

class AdsGetTargetingStatsResponse(AdsTargStats): pass

class AdsGetUploadURLResponse(Str): pass

class AdsGetVideoUploadURLResponse(Str): pass

class AdsImportTargetContactsResponse(Int): pass

class AdsRemoveOfficeUsersResponse(Bool): pass

class AdsUpdateAdsResponse(BL):
	__root__:list[int]

class AdsUpdateCampaignsResponse(Int): pass

class AdsUpdateClientsResponse(Int): pass

class AdsUpdateOfficeUsersResponse(BL):
	__root__:list["AdsUpdateOfficeUsersResult"]


class AdswebGetAdCategoriesResponse(BM):
	categories:list["AdswebGetAdCategoriesResponseCategoriesCategory"]

class AdswebGetAdUnitCodeResponse(BM):
	html:str

class AdswebGetAdUnitsResponse(BM):
	count:int
	ad_units:Optional[list["AdswebGetAdUnitsResponseAdUnitsAdUnit"]] = None

class AdswebGetFraudHistoryResponse(BM):
	count:int
	entries:Optional[list["AdswebGetFraudHistoryResponseEntriesEntry"]] = None

class AdswebGetSitesResponse(BM):
	count:int
	sites:Optional[list["AdswebGetSitesResponseSitesSite"]] = None

class AdswebGetStatisticsResponse(BM):
	next_page_id:Optional[str] = None
	items:list["AdswebGetStatisticsResponseItemsItem"]


class AppWidgetsGetAppImageUploadServerResponse(BM):
	upload_url:Optional[str] = None

class AppWidgetsGetAppImagesResponse(AppWidgetsPhotos): pass

class AppWidgetsGetGroupImageUploadServerResponse(BM):
	upload_url:Optional[str] = None

class AppWidgetsGetGroupImagesResponse(AppWidgetsPhotos): pass

class AppWidgetsGetImagesByIdResponse(BL):
	__root__:list["AppWidgetsPhoto"]

class AppWidgetsSaveAppImageResponse(AppWidgetsPhoto): pass

class AppWidgetsSaveGroupImageResponse(AppWidgetsPhoto): pass


class AppsGetCatalogResponse(AppsCatalogList): pass

class AppsGetFriendsListExtendedResponse(BM):
	count:int
	items:Optional[list["UsersUserFull"]] = None

class AppsGetFriendsListResponse(BM):
	count:int
	items:Optional[list[int]] = None

class AppsGetLeaderboardExtendedResponse(BM):
	count:Optional[int] = None
	items:Optional[list["AppsLeaderboard"]] = None
	profiles:Optional[list["UsersUser"]] = None

class AppsGetLeaderboardResponse(BM):
	count:Optional[int] = None
	items:Optional[list["AppsLeaderboard"]] = None

class AppsGetMiniAppPoliciesResponse(BM):
	privacy_policy:Optional[str] = None
	terms:Optional[str] = None

class AppsGetScopesResponse(BM):
	count:int
	items:list["AppsScope"]

class AppsGetScoreResponse(Int): pass

class AppsGetResponse(BM):
	count:Optional[int] = None
	items:Optional[list["AppsApp"]] = None

class AppsImageUploadResponse(BM):
	hash:Optional[str] = None
	image:Optional[str] = None

class AppsSendRequestResponse(Int): pass


class AuthRestoreResponse(BM):
	success:Optional[int] = None
	sid:Optional[str] = None


class BaseBoolResponse(Bool): pass

class BaseGetUploadServerResponse(BaseUploadServer): pass

class BaseOkResponse(Int): pass


class BoardAddTopicResponse(Int): pass

class BoardCreateCommentResponse(Int): pass

class BoardGetCommentsExtendedResponse(BM):
	count:int
	items:list["BoardTopicComment"]
	poll:Optional[object] = None
	profiles:list["UsersUserFull"]
	groups:list["GroupsGroupFull"]
	real_offset:Optional[int] = None

class BoardGetCommentsResponse(BM):
	count:int
	items:list["BoardTopicComment"]
	poll:Optional[object] = None
	real_offset:Optional[int] = None

class BoardGetTopicsExtendedResponse(BM):
	count:int
	items:list["BoardTopic"]
	default_order:BoardDefaultOrder
	can_add_topics:bool
	profiles:list["UsersUserFull"]
	groups:list["GroupsGroupFull"]

class BoardGetTopicsResponse(BM):
	count:int
	items:list["BoardTopic"]
	default_order:BoardDefaultOrder
	can_add_topics:bool


class DatabaseGetChairsResponse(BM):
	count:int
	items:list["BaseObject"]

class DatabaseGetCitiesByIdResponse(BL):
	__root__:list["DatabaseCityById"]

class DatabaseGetCitiesResponse(BM):
	count:int
	items:list["DatabaseCity"]

class DatabaseGetCountriesByIdResponse(BL):
	__root__:list["BaseCountry"]

class DatabaseGetCountriesResponse(BM):
	count:int
	items:list["BaseCountry"]

class DatabaseGetFacultiesResponse(BM):
	count:int
	items:list["DatabaseFaculty"]

class DatabaseGetMetroStationsByIdResponse(BL):
	__root__:list["DatabaseStation"]

class DatabaseGetMetroStationsResponse(BM):
	count:int
	items:list["DatabaseStation"]

class DatabaseGetRegionsResponse(BM):
	count:int
	items:list["DatabaseRegion"]

class DatabaseGetSchoolClassesResponse(BL):
	__root__:list[list]

class DatabaseGetSchoolsResponse(BM):
	count:int
	items:list["DatabaseSchool"]

class DatabaseGetUniversitiesResponse(BM):
	count:int
	items:list["DatabaseUniversity"]


class DocsAddResponse(Int): pass

class DocsDocUploadResponse(BM):
	file:Optional[str] = None

class DocsGetByIdResponse(BL):
	__root__:list["DocsDoc"]

class DocsGetTypesResponse(BM):
	count:Optional[int] = None
	items:Optional[list["DocsDocTypes"]] = None

class DocsGetUploadServerResponse(BaseUploadServer): pass

class DocsGetResponse(BM):
	count:int
	items:list["DocsDoc"]

class DocsSaveResponse(BM):
	type:Optional[DocsDocAttachmentType] = None
	audio_message:Optional[MessagesAudioMessage] = None
	doc:Optional[DocsDoc] = None
	graffiti:Optional[MessagesGraffiti] = None

class DocsSearchResponse(BM):
	count:int
	items:list["DocsDoc"]


class DonutGetSubscriptionResponse(DonutDonatorSubscriptionInfo): pass

class DonutGetSubscriptionsResponse(BM):
	subscriptions:list["DonutDonatorSubscriptionInfo"]
	count:Optional[int] = None
	profiles:Optional[list["UsersUserFull"]] = None
	groups:Optional[list["GroupsGroupFull"]] = None


class DownloadedGamesPaidStatusResponse(BM):
	is_paid:bool


class FaveAddTagResponse(FaveTag): pass

class FaveGetPagesResponse(BM):
	count:Optional[int] = None
	items:Optional[list["FavePage"]] = None

class FaveGetTagsResponse(BM):
	count:Optional[int] = None
	items:Optional[list["FaveTag"]] = None

class FaveGetExtendedResponse(BM):
	count:Optional[int] = None
	items:Optional[list["FaveBookmark"]] = None
	profiles:Optional[list["UsersUserFull"]] = None
	groups:Optional[list["GroupsGroup"]] = None

class FaveGetResponse(BM):
	count:Optional[int] = None
	items:Optional[list["FaveBookmark"]] = None


class FriendsAddListResponse(BM):
	list_id:int

class FriendsAddResponse(Int): pass

class FriendsAreFriendsExtendedResponse(BL):
	__root__:list["FriendsFriendExtendedStatus"]

class FriendsAreFriendsResponse(BL):
	__root__:list["FriendsFriendStatus"]

class FriendsDeleteResponse(BM):
	success:int
	friend_deleted:Optional[int] = None
	out_request_deleted:Optional[int] = None
	in_request_deleted:Optional[int] = None
	suggestion_deleted:Optional[int] = None

class FriendsGetAppUsersResponse(BL):
	__root__:list[int]

class FriendsGetByPhonesResponse(BL):
	__root__:list["FriendsUserXtrPhone"]

class FriendsGetListsResponse(BM):
	count:int
	items:list["FriendsFriendsList"]

class FriendsGetMutualResponse(BL):
	__root__:list[int]

class FriendsGetMutualTargetUidsResponse(BL):
	__root__:list["FriendsMutualFriend"]

class FriendsGetOnlineOnlineMobileResponse(BM):
	online:list[int]
	online_mobile:list[int]

class FriendsGetOnlineResponse(BL):
	__root__:list[int]

class FriendsGetRecentResponse(BL):
	__root__:list[int]

class FriendsGetRequestsExtendedResponse(BM):
	count:Optional[int] = None
	items:Optional[list["FriendsRequestsXtrMessage"]] = None

class FriendsGetRequestsNeedMutualResponse(BM):
	count:Optional[int] = None
	items:Optional[list["FriendsRequests"]] = None

class FriendsGetRequestsResponse(BM):
	count:Optional[int] = None
	items:Optional[list[int]] = None
	count_unread:Optional[int] = None

class FriendsGetSuggestionsResponse(BM):
	count:int
	items:list["UsersUserFull"]

class FriendsGetFieldsResponse(BM):
	count:int
	items:list["UsersUserFull"]

class FriendsGetResponse(BM):
	count:int
	items:list[int]

class FriendsSearchResponse(BM):
	count:int
	items:list["UsersUserFull"]


class GiftsGetResponse(BM):
	count:Optional[int] = None
	items:Optional[list["GiftsGift"]] = None


class GroupsAddAddressResponse(GroupsAddress): pass

class GroupsAddCallbackServerResponse(BM):
	server_id:int

class GroupsAddLinkResponse(GroupsLinksItem): pass

class GroupsCreateResponse(GroupsGroup): pass

class GroupsEditAddressResponse(GroupsAddress): pass

class GroupsGetAddressesResponse(BM):
	count:int
	items:list["GroupsAddress"]

class GroupsGetBannedResponse(BM):
	count:int
	items:list["GroupsBannedItem"]

class GroupsGetByIdObjectLegacyResponse(BL):
	__root__:list["GroupsGroupFull"]

class GroupsGetCallbackConfirmationCodeResponse(BM):
	code:str

class GroupsGetCallbackServersResponse(BM):
	count:int
	items:list["GroupsCallbackServer"]

class GroupsGetCallbackSettingsResponse(GroupsCallbackSettings): pass

class GroupsGetCatalogInfoExtendedResponse(BM):
	enabled:bool
	categories:Optional[list["GroupsGroupCategoryFull"]] = None

class GroupsGetCatalogInfoResponse(BM):
	enabled:bool
	categories:Optional[list["GroupsGroupCategory"]] = None

class GroupsGetCatalogResponse(BM):
	count:int
	items:list["GroupsGroup"]

class GroupsGetInvitedUsersResponse(BM):
	count:int
	items:list["UsersUserFull"]

class GroupsGetInvitesExtendedResponse(BM):
	count:int
	items:list["GroupsGroupFull"]
	profiles:list["UsersUserMin"]
	groups:list["GroupsGroupFull"]

class GroupsGetInvitesResponse(BM):
	count:int
	items:list["GroupsGroupFull"]

class GroupsGetLongPollServerResponse(GroupsLongPollServer): pass

class GroupsGetLongPollSettingsResponse(GroupsLongPollSettings): pass

class GroupsGetMembersFieldsResponse(BM):
	count:int
	items:list["GroupsUserXtrRole"]

class GroupsGetMembersFilterResponse(BM):
	count:int
	items:list["GroupsMemberRole"]

class GroupsGetMembersResponse(BM):
	count:int
	items:list[int]

class GroupsGetRequestsFieldsResponse(BM):
	count:int
	items:list["UsersUserFull"]

class GroupsGetRequestsResponse(BM):
	count:int
	items:list[int]

class GroupsGetSettingsResponse(BM):
	access:Optional[GroupsGroupAccess] = None
	address:Optional[str] = None
	audio:GroupsGroupAudio
	articles:int
	recognize_photo:Optional[int] = None
	city_id:int
	city_name:str
	contacts:Optional[bool] = None
	links:Optional[bool] = None
	sections_list:Optional[list["GroupsSectionsListItem"]] = None
	main_section:Optional[GroupsGroupFullSection] = None
	secondary_section:Optional[GroupsGroupFullSection] = None
	age_limits:Optional[GroupsGroupAgeLimits] = None
	country_id:int
	country_name:str
	description:str
	docs:GroupsGroupDocs
	events:Optional[bool] = None
	obscene_filter:bool
	obscene_stopwords:bool
	obscene_words:list[str]
	event_group_id:Optional[int] = None
	photos:GroupsGroupPhotos
	public_category:Optional[int] = None
	public_category_list:Optional[list["GroupsGroupPublicCategoryList"]] = None
	public_date:Optional[str] = None
	public_date_label:Optional[str] = None
	public_subcategory:Optional[int] = None
	rss:Optional[str] = None
	start_date:Optional[int] = None
	finish_date:Optional[int] = None
	subject:Optional[int] = None
	subject_list:Optional[list["GroupsSubjectItem"]] = None
	suggested_privacy:Optional[GroupsGroupSuggestedPrivacy] = None
	title:str
	topics:GroupsGroupTopics
	twitter:Optional[GroupsSettingsTwitter] = None
	video:GroupsGroupVideo
	wall:GroupsGroupWall
	website:Optional[str] = None
	phone:Optional[str] = None
	email:Optional[str] = None
	wiki:GroupsGroupWiki

class GroupsGetTagListResponse(BL):
	__root__:list["GroupsGroupTag"]

class GroupsGetTokenPermissionsResponse(BM):
	mask:int
	permissions:list["GroupsTokenPermissionSetting"]

class GroupsGetObjectExtendedResponse(BM):
	count:int
	items:list["GroupsGroupFull"]

class GroupsGetResponse(BM):
	count:int
	items:list[int]

class GroupsIsMemberExtendedResponse(BM):
	member:bool
	invitation:Optional[bool] = None
	can_invite:Optional[bool] = None
	can_recall:Optional[bool] = None
	request:Optional[bool] = None

class GroupsIsMemberResponse(Bool): pass

class GroupsIsMemberUserIdsExtendedResponse(BL):
	__root__:list["GroupsMemberStatusFull"]

class GroupsIsMemberUserIdsResponse(BL):
	__root__:list["GroupsMemberStatus"]

class GroupsSearchResponse(BM):
	count:int
	items:list["GroupsGroup"]


class LeadFormsCreateResponse(BM):
	form_id:int
	url:str

class LeadFormsDeleteResponse(BM):
	form_id:int

class LeadFormsGetLeadsResponse(BM):
	leads:list["LeadFormsLead"]
	next_page_token:Optional[str] = None

class LeadFormsGetResponse(LeadFormsForm): pass

class LeadFormsListResponse(BL):
	__root__:list["LeadFormsForm"]

class LeadFormsUploadUrlResponse(Str): pass


class LikesAddResponse(BM):
	likes:int

class LikesDeleteResponse(BM):
	likes:int

class LikesGetListExtendedResponse(BM):
	count:int
	items:list["UsersUserMin"]

class LikesGetListResponse(BM):
	count:int
	items:list[int]

class LikesIsLikedResponse(BM):
	liked:bool
	copied:bool


class MarketAddAlbumResponse(BM):
	market_album_id:Optional[int] = None
	albums_count:Optional[int] = None

class MarketAddResponse(BM):
	market_item_id:int

class MarketCreateCommentResponse(Int): pass

class MarketDeleteCommentResponse(Bool): pass

class MarketGetAlbumByIdResponse(BM):
	count:Optional[int] = None
	items:Optional[list["MarketMarketAlbum"]] = None

class MarketGetAlbumsResponse(BM):
	count:Optional[int] = None
	items:Optional[list["MarketMarketAlbum"]] = None

class MarketGetByIdExtendedResponse(BM):
	count:Optional[int] = None
	items:Optional[list["MarketMarketItemFull"]] = None

class MarketGetByIdResponse(BM):
	count:Optional[int] = None
	items:Optional[list["MarketMarketItem"]] = None

class MarketGetCategoriesNewResponse(BM):
	items:list["MarketMarketCategoryTree"]

class MarketGetCategoriesResponse(BM):
	count:Optional[int] = None
	items:Optional[list["MarketMarketCategory"]] = None

class MarketGetCommentsResponse(BM):
	count:Optional[int] = None
	items:Optional[list["WallWallComment"]] = None

class MarketGetGroupOrdersResponse(BM):
	count:int
	items:list["MarketOrder"]

class MarketGetOrderByIdResponse(BM):
	order:Optional[MarketOrder] = None

class MarketGetOrderItemsResponse(BM):
	count:int
	items:list["MarketOrderItem"]

class MarketGetOrdersExtendedResponse(BM):
	count:int
	items:list["MarketOrder"]
	groups:Optional[list["GroupsGroupFull"]] = None

class MarketGetOrdersResponse(BM):
	count:int
	items:list["MarketOrder"]

class MarketGetExtendedResponse(BM):
	count:Optional[int] = None
	items:Optional[list["MarketMarketItemFull"]] = None
	variants:Optional[list["MarketMarketItemFull"]] = None

class MarketGetResponse(BM):
	count:Optional[int] = None
	items:Optional[list["MarketMarketItem"]] = None
	variants:Optional[list["MarketMarketItem"]] = None

class MarketRestoreCommentResponse(Bool): pass

class MarketSearchExtendedResponse(BM):
	count:int
	view_type:MarketServicesViewType
	items:list["MarketMarketItemFull"]
	variants:Optional[list["MarketMarketItemFull"]] = None

class MarketSearchResponse(BM):
	count:int
	view_type:MarketServicesViewType
	items:list["MarketMarketItem"]
	variants:Optional[list["MarketMarketItem"]] = None
	groups:Optional[list["GroupsGroupFull"]] = None


class MessagesCreateChatResponse(Int): pass

class MessagesDeleteChatPhotoResponse(BM):
	message_id:Optional[int] = None
	chat:Optional[MessagesChat] = None

class MessagesDeleteConversationResponse(BM):
	last_deleted_id:int

class MessagesDeleteResponse(Bool): pass

class MessagesEditResponse(Bool): pass

class MessagesGetByConversationMessageIdExtendedResponse(BM):
	count:int
	items:list["MessagesMessage"]
	profiles:Optional[list["UsersUserFull"]] = None
	groups:Optional[list["GroupsGroupFull"]] = None

class MessagesGetByConversationMessageIdResponse(BM):
	count:int
	items:list["MessagesMessage"]

class MessagesGetByIdExtendedResponse(BM):
	count:int
	items:list["MessagesMessage"]
	profiles:list["UsersUserFull"]
	groups:Optional[list["GroupsGroupFull"]] = None

class MessagesGetByIdResponse(BM):
	count:int
	items:list["MessagesMessage"]

class MessagesGetChatPreviewResponse(BM):
	preview:Optional[MessagesChatPreview] = None
	profiles:Optional[list["UsersUserFull"]] = None
	groups:Optional[list["GroupsGroupFull"]] = None

class MessagesGetChatChatIdsFieldsResponse(BL):
	__root__:list["MessagesChatFull"]

class MessagesGetChatChatIdsResponse(BL):
	__root__:list["MessagesChat"]

class MessagesGetChatFieldsResponse(MessagesChatFull): pass

class MessagesGetChatResponse(MessagesChat): pass

class MessagesGetConversationMembersResponse(MessagesGetConversationMembers): pass

class MessagesGetConversationsByIdExtendedResponse(MessagesGetConversationByIdExtended): pass

class MessagesGetConversationsByIdResponse(MessagesGetConversationById): pass

class MessagesGetConversationsResponse(BM):
	count:int
	unread_count:Optional[int] = None
	items:list["MessagesConversationWithMessage"]
	profiles:Optional[list["UsersUserFull"]] = None
	groups:Optional[list["GroupsGroupFull"]] = None

class MessagesGetHistoryAttachmentsResponse(BM):
	items:Optional[list["MessagesHistoryAttachment"]] = None
	next_from:Optional[str] = None
	profiles:Optional[list["UsersUserFull"]] = None
	groups:Optional[list["GroupsGroupFull"]] = None

class MessagesGetHistoryExtendedResponse(BM):
	count:int
	items:list["MessagesMessage"]
	profiles:Optional[list["UsersUserFull"]] = None
	groups:Optional[list["GroupsGroupFull"]] = None
	conversations:Optional[list["MessagesConversation"]] = None

class MessagesGetHistoryResponse(BM):
	count:int
	items:list["MessagesMessage"]

class MessagesGetImportantMessagesExtendedResponse(BM):
	messages:MessagesMessagesArray
	profiles:Optional[list["UsersUserFull"]] = None
	groups:Optional[list["GroupsGroupFull"]] = None
	conversations:Optional[list["MessagesConversation"]] = None

class MessagesGetImportantMessagesResponse(BM):
	messages:MessagesMessagesArray
	profiles:Optional[list["UsersUser"]] = None
	groups:Optional[list["GroupsGroupFull"]] = None
	conversations:Optional[list["MessagesConversation"]] = None

class MessagesGetIntentUsersResponse(BM):
	count:int
	items:list[int]
	profiles:Optional[list["UsersUserFull"]] = None

class MessagesGetInviteLinkResponse(BM):
	link:Optional[str] = None

class MessagesGetLastActivityResponse(MessagesLastActivity): pass

class MessagesGetLongPollHistoryResponse(BM):
	history:Optional[list[list]] = None
	messages:Optional[MessagesLongpollMessages] = None
	credentials:Optional[MessagesLongpollParams] = None
	profiles:Optional[list["UsersUserFull"]] = None
	groups:Optional[list["GroupsGroupFull"]] = None
	chats:Optional[list["MessagesChat"]] = None
	new_pts:Optional[int] = None
	from_pts:Optional[int] = None
	more:Optional[bool] = None
	conversations:Optional[list["MessagesConversation"]] = None

class MessagesGetLongPollServerResponse(MessagesLongpollParams): pass

class MessagesIsMessagesFromGroupAllowedResponse(BM):
	is_allowed:Optional[bool] = None

class MessagesJoinChatByInviteLinkResponse(BM):
	chat_id:Optional[int] = None

class MessagesMarkAsImportantResponse(BL):
	__root__:list[int]

class MessagesPinResponse(MessagesPinnedMessage): pass

class MessagesSearchConversationsExtendedResponse(BM):
	count:int
	items:list["MessagesConversation"]
	profiles:Optional[list["UsersUserFull"]] = None
	groups:Optional[list["GroupsGroupFull"]] = None

class MessagesSearchConversationsResponse(BM):
	count:int
	items:list["MessagesConversation"]

class MessagesSearchExtendedResponse(BM):
	count:int
	items:list["MessagesMessage"]
	profiles:Optional[list["UsersUserFull"]] = None
	groups:Optional[list["GroupsGroupFull"]] = None
	conversations:Optional[list["MessagesConversation"]] = None

class MessagesSearchResponse(BM):
	count:int
	items:list["MessagesMessage"]

class MessagesSendResponse(Int): pass

class MessagesSendUserIdsResponse(BL):
	__root__:list["MessagesSendUserIdsResponseItem"]

class MessagesSetChatPhotoResponse(BM):
	message_id:Optional[int] = None
	chat:Optional[MessagesChat] = None


class NewsfeedGenericResponse(BM):
	items:list["NewsfeedNewsfeedItem"]
	profiles:list["UsersUserFull"]
	groups:list["GroupsGroupFull"]
	new_returned_news_items_count:Optional[int] = None

class NewsfeedGetBannedExtendedResponse(BM):
	profiles:Optional[list["UsersUserFull"]] = None
	groups:Optional[list["GroupsGroupFull"]] = None

class NewsfeedGetBannedResponse(BM):
	groups:Optional[list[int]] = None
	members:Optional[list[int]] = None

class NewsfeedGetCommentsResponse(BM):
	items:list["NewsfeedNewsfeedItem"]
	profiles:list["UsersUserFull"]
	groups:list["GroupsGroupFull"]
	next_from:Optional[str] = None

class NewsfeedGetListsExtendedResponse(BM):
	count:int
	items:list["NewsfeedListFull"]

class NewsfeedGetListsResponse(BM):
	count:int
	items:list["NewsfeedList"]

class NewsfeedGetMentionsResponse(BM):
	count:int
	items:list["WallWallpostToId"]

class NewsfeedGetSuggestedSourcesResponse(BM):
	count:Optional[int] = None
	items:Optional[list["UsersSubscriptionsItem"]] = None

class NewsfeedIgnoreItemResponse(BM):
	status:bool

class NewsfeedSaveListResponse(Int): pass

class NewsfeedSearchExtendedResponse(BM):
	items:Optional[list["WallWallpostFull"]] = None
	profiles:Optional[list["UsersUserFull"]] = None
	groups:Optional[list["GroupsGroupFull"]] = None
	suggested_queries:Optional[list[str]] = None
	next_from:Optional[str] = None
	count:Optional[int] = None
	total_count:Optional[int] = None

class NewsfeedSearchResponse(BM):
	items:Optional[list["WallWallpostFull"]] = None
	suggested_queries:Optional[list[str]] = None
	next_from:Optional[str] = None
	count:Optional[int] = None
	total_count:Optional[int] = None


class NotesAddResponse(Int): pass

class NotesCreateCommentResponse(Int): pass

class NotesGetByIdResponse(NotesNote): pass

class NotesGetCommentsResponse(BM):
	count:int
	items:list["NotesNoteComment"]

class NotesGetResponse(BM):
	count:int
	items:list["NotesNote"]


class NotificationsGetResponse(BM):
	count:Optional[int] = None
	items:Optional[list["NotificationsNotificationItem"]] = None
	profiles:Optional[list["UsersUser"]] = None
	groups:Optional[list["GroupsGroup"]] = None
	last_viewed:Optional[int] = None
	photos:Optional[list["PhotosPhoto"]] = None
	videos:Optional[list["VideoVideo"]] = None
	apps:Optional[list["AppsApp"]] = None
	next_from:Optional[str] = None
	ttl:Optional[int] = None

class NotificationsMarkAsViewedResponse(Bool): pass

class NotificationsSendMessageResponse(BL):
	__root__:list["NotificationsSendMessageItem"]


class OrdersCancelSubscriptionResponse(Bool): pass

class OrdersChangeStateResponse(Str): pass

class OrdersGetAmountResponse(BL):
	__root__:list["OrdersAmount"]

class OrdersGetByIdResponse(BL):
	__root__:list["OrdersOrder"]

class OrdersGetUserSubscriptionByIdResponse(OrdersSubscription): pass

class OrdersGetUserSubscriptionsResponse(BM):
	count:Optional[int] = None
	items:Optional[list["OrdersSubscription"]] = None

class OrdersGetResponse(BL):
	__root__:list["OrdersOrder"]

class OrdersUpdateSubscriptionResponse(Bool): pass


class PagesGetHistoryResponse(BL):
	__root__:list["PagesWikipageHistory"]

class PagesGetTitlesResponse(BL):
	__root__:list["PagesWikipage"]

class PagesGetVersionResponse(PagesWikipageFull): pass

class PagesGetResponse(PagesWikipageFull): pass

class PagesParseWikiResponse(Str): pass

class PagesSaveAccessResponse(Int): pass

class PagesSaveResponse(Int): pass


class PhotosCopyResponse(Int): pass

class PhotosCreateAlbumResponse(PhotosPhotoAlbumFull): pass

class PhotosCreateCommentResponse(Int): pass

class PhotosDeleteCommentResponse(Bool): pass

class PhotosGetAlbumsCountResponse(Int): pass

class PhotosGetAlbumsResponse(BM):
	count:int
	items:list["PhotosPhotoAlbumFull"]

class PhotosGetAllCommentsResponse(BM):
	count:Optional[int] = None
	items:Optional[list["WallWallComment"]] = None

class PhotosGetAllExtendedResponse(BM):
	count:Optional[int] = None
	items:Optional[list["PhotosPhotoFullXtrRealOffset"]] = None
	more:Optional[bool] = None

class PhotosGetAllResponse(BM):
	count:Optional[int] = None
	items:Optional[list["PhotosPhotoXtrRealOffset"]] = None
	more:Optional[bool] = None

class PhotosGetByIdResponse(BL):
	__root__:list["PhotosPhoto"]

class PhotosGetCommentsExtendedResponse(BM):
	count:int
	real_offset:Optional[int] = None
	items:list["WallWallComment"]
	profiles:list["UsersUserFull"]
	groups:list["GroupsGroupFull"]

class PhotosGetCommentsResponse(BM):
	count:Optional[int] = None
	real_offset:Optional[int] = None
	items:Optional[list["WallWallComment"]] = None

class PhotosGetMarketUploadServerResponse(BaseUploadServer): pass

class PhotosGetMessagesUploadServerResponse(PhotosPhotoUpload): pass

class PhotosGetNewTagsResponse(BM):
	count:int
	items:list["PhotosPhotoXtrTagInfo"]

class PhotosGetTagsResponse(BL):
	__root__:list["PhotosPhotoTag"]

class PhotosGetUploadServerResponse(PhotosPhotoUpload): pass

class PhotosGetUserPhotosResponse(BM):
	count:int
	items:list["PhotosPhoto"]

class PhotosGetWallUploadServerResponse(PhotosPhotoUpload): pass

class PhotosGetResponse(BM):
	count:int
	items:list["PhotosPhoto"]

class PhotosMarketAlbumUploadResponse(BM):
	gid:Optional[int] = None
	hash:Optional[str] = None
	photo:Optional[str] = None
	server:Optional[int] = None

class PhotosMarketUploadResponse(BM):
	crop_data:Optional[str] = None
	crop_hash:Optional[str] = None
	group_id:Optional[int] = None
	hash:Optional[str] = None
	photo:Optional[str] = None
	server:Optional[int] = None

class PhotosMessageUploadResponse(BM):
	hash:Optional[str] = None
	photo:Optional[str] = None
	server:Optional[int] = None

class PhotosOwnerCoverUploadResponse(BM):
	hash:Optional[str] = None
	photo:Optional[str] = None

class PhotosOwnerUploadResponse(BM):
	hash:Optional[str] = None
	photo:Optional[str] = None
	server:Optional[int] = None

class PhotosPhotoUploadResponse(BM):
	aid:Optional[int] = None
	hash:Optional[str] = None
	photo:Optional[str] = None
	photos_list:Optional[str] = None
	server:Optional[int] = None

class PhotosPutTagResponse(Int): pass

class PhotosRestoreCommentResponse(Bool): pass

class PhotosSaveMarketAlbumPhotoResponse(BL):
	__root__:list["PhotosPhoto"]

class PhotosSaveMarketPhotoResponse(BL):
	__root__:list["PhotosPhoto"]

class PhotosSaveMessagesPhotoResponse(BL):
	__root__:list["PhotosPhoto"]

class PhotosSaveOwnerCoverPhotoResponse(BM):
	images:Optional[list["BaseImage"]] = None

class PhotosSaveOwnerPhotoResponse(BM):
	photo_hash:str
	photo_src:str
	photo_src_big:Optional[str] = None
	photo_src_small:Optional[str] = None
	saved:Optional[int] = None
	post_id:Optional[int] = None

class PhotosSaveWallPhotoResponse(BL):
	__root__:list["PhotosPhoto"]

class PhotosSaveResponse(BL):
	__root__:list["PhotosPhoto"]

class PhotosSearchResponse(BM):
	count:Optional[int] = None
	items:Optional[list["PhotosPhoto"]] = None

class PhotosWallUploadResponse(BM):
	hash:Optional[str] = None
	photo:Optional[str] = None
	server:Optional[int] = None


class PodcastsSearchPodcastResponse(BM):
	podcasts:list["PodcastExternalData"]
	results_total:int


class PollsAddVoteResponse(Bool): pass

class PollsCreateResponse(PollsPoll): pass

class PollsDeleteVoteResponse(Bool): pass

class PollsGetBackgroundsResponse(BL):
	__root__:list["PollsBackground"]

class PollsGetByIdResponse(PollsPoll): pass

class PollsGetVotersResponse(BL):
	__root__:list["PollsVoters"]

class PollsSavePhotoResponse(PollsBackground): pass


class PrettyCardsCreateResponse(BM):
	owner_id:int
	card_id:str

class PrettyCardsDeleteResponse(BM):
	owner_id:int
	card_id:str
	error:Optional[str] = None

class PrettyCardsEditResponse(BM):
	owner_id:int
	card_id:str

class PrettyCardsGetByIdResponse(BL):
	__root__:list["PrettyCardsPrettyCardOrError"]

class PrettyCardsGetUploadURLResponse(Str): pass

class PrettyCardsGetResponse(BM):
	count:int
	items:list["PrettyCardsPrettyCard"]


class SearchGetHintsResponse(BM):
	count:int
	items:list["SearchHint"]
	suggested_queries:Optional[list[str]] = None


class SecureCheckTokenResponse(SecureTokenChecked): pass

class SecureGetAppBalanceResponse(Int): pass

class SecureGetSMSHistoryResponse(BL):
	__root__:list["SecureSmsNotification"]

class SecureGetTransactionsHistoryResponse(BL):
	__root__:list["SecureTransaction"]

class SecureGetUserLevelResponse(BL):
	__root__:list["SecureLevel"]

class SecureGiveEventStickerResponse(BL):
	__root__:list["SecureGiveEventStickerItem"]

class SecureSendNotificationResponse(BL):
	__root__:list[int]

class SecureSetCounterArrayResponse(BL):
	__root__:list["SecureSetCounterItem"]


class StatsGetPostReachResponse(BL):
	__root__:list["StatsWallpostStat"]

class StatsGetResponse(BL):
	__root__:list["StatsPeriod"]


class StatusGetResponse(StatusStatus): pass


class StorageGetKeysResponse(BL):
	__root__:list[str]

class StorageGetResponse(BL):
	__root__:list["StorageValue"]


class StoreGetFavoriteStickersResponse(BL):
	__root__:list["BaseSticker"]

class StoreGetProductsResponse(BL):
	__root__:list["StoreProduct"]

class StoreGetStickersKeywordsResponse(BM):
	count:int
	dictionary:list["StoreStickersKeyword"]
	chunks_count:Optional[int] = None
	chunks_hash:Optional[str] = None


class StoriesGetBannedExtendedResponse(BM):
	count:int
	items:list[int]
	profiles:list["UsersUserFull"]
	groups:list["GroupsGroupFull"]

class StoriesGetBannedResponse(BM):
	count:int
	items:list[int]

class StoriesGetByIdExtendedResponse(BM):
	count:int
	items:list["StoriesStory"]
	profiles:list["UsersUserFull"]
	groups:list["GroupsGroupFull"]

class StoriesGetPhotoUploadServerResponse(BM):
	upload_url:str
	user_ids:list[int]

class StoriesGetStatsResponse(StoriesStoryStats): pass

class StoriesGetVideoUploadServerResponse(BM):
	upload_url:str
	user_ids:list[int]

class StoriesGetViewersExtendedV5115Response(BM):
	count:int
	items:list["StoriesViewersItem"]
	hidden_reason:Optional[str] = None
	next_from:Optional[str] = None

class StoriesGetViewersExtendedResponse(BM):
	count:int
	items:list["UsersUserFull"]

class StoriesGetV5113Response(BM):
	count:int
	items:list["StoriesFeedItem"]
	profiles:Optional[list["UsersUserFull"]] = None
	groups:Optional[list["GroupsGroup"]] = None
	need_upload_screen:Optional[bool] = None

class StoriesGetResponse(BM):
	count:int
	items:list[list]
	promo_data:Optional[StoriesPromoBlock] = None
	profiles:Optional[list["UsersUserFull"]] = None
	groups:Optional[list["GroupsGroup"]] = None
	need_upload_screen:Optional[bool] = None

class StoriesSaveResponse(BM):
	count:int
	items:list["StoriesStory"]
	profiles:Optional[list["UsersUser"]] = None
	groups:Optional[list["GroupsGroup"]] = None

class StoriesUploadResponse(BM):
	upload_result:Optional[str] = None


class StreamingGetServerUrlResponse(BM):
	endpoint:Optional[str] = None
	key:Optional[str] = None


class UsersGetFollowersFieldsResponse(BM):
	count:int
	items:list["UsersUserFull"]

class UsersGetFollowersResponse(BM):
	count:int
	items:list[int]

class UsersGetSubscriptionsExtendedResponse(BM):
	count:int
	items:list["UsersSubscriptionsItem"]

class UsersGetSubscriptionsResponse(BM):
	users:UsersUsersArray
	groups:GroupsGroupsArray

class UsersGetResponse(BL):
	__root__:list["UsersUserFull"]

class UsersSearchResponse(BM):
	count:int
	items:list["UsersUserFull"]


class UtilsCheckLinkResponse(UtilsLinkChecked): pass

class UtilsGetLastShortenedLinksResponse(BM):
	count:Optional[int] = None
	items:Optional[list["UtilsLastShortenedLink"]] = None

class UtilsGetLinkStatsExtendedResponse(UtilsLinkStatsExtended): pass

class UtilsGetLinkStatsResponse(UtilsLinkStats): pass

class UtilsGetServerTimeResponse(Int): pass

class UtilsGetShortLinkResponse(UtilsShortLink): pass

class UtilsResolveScreenNameResponse(UtilsDomainResolved): pass


class VideoAddAlbumResponse(BM):
	album_id:int

class VideoChangeVideoAlbumsResponse(BL):
	__root__:list[int]

class VideoCreateCommentResponse(Int): pass

class VideoGetAlbumByIdResponse(VideoVideoAlbumFull): pass

class VideoGetAlbumsByVideoExtendedResponse(BM):
	count:Optional[int] = None
	items:Optional[list["VideoVideoAlbumFull"]] = None

class VideoGetAlbumsByVideoResponse(BL):
	__root__:list[int]

class VideoGetAlbumsExtendedResponse(BM):
	count:int
	items:list["VideoVideoAlbumFull"]

class VideoGetAlbumsResponse(BM):
	count:int
	items:list["VideoVideoAlbum"]

class VideoGetCommentsExtendedResponse(BM):
	count:int
	items:list["WallWallComment"]
	profiles:list["UsersUser"]
	groups:list["GroupsGroup"]
	current_level_count:Optional[int] = None
	can_post:Optional[bool] = None
	show_reply_button:Optional[bool] = None
	groups_can_post:Optional[bool] = None
	real_offset:Optional[int] = None

class VideoGetCommentsResponse(BM):
	count:int
	items:list["WallWallComment"]
	current_level_count:Optional[int] = None
	can_post:Optional[bool] = None
	show_reply_button:Optional[bool] = None
	groups_can_post:Optional[bool] = None
	real_offset:Optional[int] = None

class VideoGetResponse(BM):
	count:int
	items:list["VideoVideoFull"]
	profiles:Optional[list["UsersUserFull"]] = None
	groups:Optional[list["GroupsGroupFull"]] = None

class VideoRestoreCommentResponse(Bool): pass

class VideoSaveResponse(VideoSaveResult): pass

class VideoSearchExtendedResponse(BM):
	count:int
	items:list["VideoVideoFull"]
	profiles:list["UsersUser"]
	groups:list["GroupsGroupFull"]

class VideoSearchResponse(BM):
	count:int
	items:list["VideoVideoFull"]

class VideoUploadResponse(BM):
	size:Optional[int] = None
	video_id:Optional[int] = None


class WallCreateCommentResponse(BM):
	comment_id:int

class WallEditResponse(BM):
	post_id:int

class WallGetByIdExtendedResponse(BM):
	items:list["WallWallpostFull"]
	profiles:list["UsersUserFull"]
	groups:list["GroupsGroupFull"]

class WallGetByIdLegacyResponse(BL):
	__root__:list["WallWallpostFull"]

class WallGetByIdResponse(BM):
	items:Optional[list["WallWallpostFull"]] = None

class WallGetCommentExtendedResponse(BM):
	items:list["WallWallComment"]
	profiles:list["UsersUser"]
	groups:list["GroupsGroup"]

class WallGetCommentResponse(BM):
	items:list["WallWallComment"]

class WallGetCommentsExtendedResponse(BM):
	count:int
	items:list["WallWallComment"]
	profiles:list["UsersUser"]
	groups:list["GroupsGroup"]
	current_level_count:Optional[int] = None
	can_post:Optional[bool] = None
	show_reply_button:Optional[bool] = None
	groups_can_post:Optional[bool] = None

class WallGetCommentsResponse(BM):
	count:int
	items:list["WallWallComment"]
	current_level_count:Optional[int] = None
	can_post:Optional[bool] = None
	show_reply_button:Optional[bool] = None
	groups_can_post:Optional[bool] = None

class WallGetRepostsResponse(BM):
	items:list["WallWallpostFull"]
	profiles:list["UsersUser"]
	groups:list["GroupsGroup"]

class WallGetExtendedResponse(BM):
	count:int
	items:list["WallWallpostFull"]
	profiles:list["UsersUserFull"]
	groups:list["GroupsGroupFull"]

class WallGetResponse(BM):
	count:int
	items:list["WallWallpostFull"]

class WallPostAdsStealthResponse(BM):
	post_id:int

class WallPostResponse(BM):
	post_id:int

class WallRepostResponse(BM):
	success:int
	post_id:int
	reposts_count:int
	wall_repost_count:Optional[int] = None
	mail_repost_count:Optional[int] = None
	likes_count:int

class WallSearchExtendedResponse(BM):
	count:int
	items:list["WallWallpostFull"]
	profiles:list["UsersUserFull"]
	groups:list["GroupsGroupFull"]

class WallSearchResponse(BM):
	count:int
	items:list["WallWallpostFull"]


class WidgetsGetCommentsResponse(BM):
	count:int
	posts:list["WidgetsWidgetComment"]

class WidgetsGetPagesResponse(BM):
	count:int
	pages:list["WidgetsWidgetPage"]


