from typing import Optional
from .base import BaseMethod, GetResponseHandlerException
from .objects import *
from .responses import *

class Account(BaseMethod):
	def __init__(self, vk):
		super().__init__(vk)

	async def ban(self, owner_id:Optional[int]=None) -> BaseOkResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("account.ban", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def changePassword(self, restore_sid:Optional[str]=None, change_password_hash:Optional[str]=None, old_password:Optional[str]=None, new_password:Optional[str]=None) -> AccountChangePasswordResponse:
		"""Changes a user password after access is successfully restored with the [vk.com/dev/auth.restore|auth.restore] method."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("account.changePassword", **args)
		models = [AccountChangePasswordResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getActiveOffers(self, offset:Optional[int]=None, count:Optional[int]=None) -> AccountGetActiveOffersResponse:
		"""Returns a list of active ads (offers) which executed by the user will bring him/her respective number of votes to his balance in the application."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("account.getActiveOffers", **args)
		models = [AccountGetActiveOffersResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getAppPermissions(self, user_id:Optional[int]=None) -> AccountGetAppPermissionsResponse:
		"""Gets settings of the user in this application."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("account.getAppPermissions", **args)
		models = [AccountGetAppPermissionsResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getBanned(self, offset:Optional[int]=None, count:Optional[int]=None) -> AccountGetBannedResponse:
		"""Returns a user's blacklist."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("account.getBanned", **args)
		models = [AccountGetBannedResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getCounters(self, filter:Optional[list]=None, user_id:Optional[int]=None) -> AccountGetCountersResponse:
		"""Returns non-null values of user counters."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("account.getCounters", **args)
		models = [AccountGetCountersResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getInfo(self, fields:Optional[list]=None) -> AccountGetInfoResponse:
		"""Returns current account info."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("account.getInfo", **args)
		models = [AccountGetInfoResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getProfileInfo(self) -> AccountGetProfileInfoResponse:
		"""Returns the current account info."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("account.getProfileInfo", **args)
		models = [AccountGetProfileInfoResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getPushSettings(self, device_id:Optional[str]=None) -> AccountGetPushSettingsResponse:
		"""Gets settings of push notifications."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("account.getPushSettings", **args)
		models = [AccountGetPushSettingsResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def registerDevice(self, token:Optional[str]=None, device_model:Optional[str]=None, device_year:Optional[int]=None, device_id:Optional[str]=None, system_version:Optional[str]=None, settings:Optional[str]=None, sandbox:Optional[bool]=None) -> BaseOkResponse:
		"""Subscribes an iOS/Android/Windows Phone-based device to receive push notifications"""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("account.registerDevice", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def saveProfileInfo(self, first_name:Optional[str]=None, last_name:Optional[str]=None, maiden_name:Optional[str]=None, screen_name:Optional[str]=None, cancel_request_id:Optional[int]=None, sex:Optional[int]=None, relation:Optional[int]=None, relation_partner_id:Optional[int]=None, bdate:Optional[str]=None, bdate_visibility:Optional[int]=None, home_town:Optional[str]=None, country_id:Optional[int]=None, city_id:Optional[int]=None, status:Optional[str]=None) -> AccountSaveProfileInfoResponse:
		"""Edits current profile info."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("account.saveProfileInfo", **args)
		models = [AccountSaveProfileInfoResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def setInfo(self, name:Optional[str]=None, value:Optional[str]=None) -> BaseOkResponse:
		"""Allows to edit the current account info."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("account.setInfo", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def setOffline(self) -> BaseOkResponse:
		"""Marks a current user as offline."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("account.setOffline", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def setOnline(self, voip:Optional[bool]=None) -> BaseOkResponse:
		"""Marks the current user as online for 15 minutes."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("account.setOnline", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def setPushSettings(self, device_id:Optional[str]=None, settings:Optional[str]=None, key:Optional[str]=None, value:Optional[list]=None) -> BaseOkResponse:
		"""Change push settings."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("account.setPushSettings", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def setSilenceMode(self, device_id:Optional[str]=None, time:Optional[int]=None, peer_id:Optional[int]=None, sound:Optional[int]=None) -> BaseOkResponse:
		"""Mutes push notifications for the set period of time."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("account.setSilenceMode", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def unban(self, owner_id:Optional[int]=None) -> BaseOkResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("account.unban", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def unregisterDevice(self, device_id:Optional[str]=None, sandbox:Optional[bool]=None) -> BaseOkResponse:
		"""Unsubscribes a device from push notifications."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("account.unregisterDevice", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)



class Ads(BaseMethod):
	def __init__(self, vk):
		super().__init__(vk)

	async def addOfficeUsers(self, account_id:Optional[int]=None, data:Optional[str]=None) -> AdsAddOfficeUsersResponse:
		"""Adds managers and/or supervisors to advertising account."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("ads.addOfficeUsers", **args)
		models = [AdsAddOfficeUsersResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def checkLink(self, account_id:Optional[int]=None, link_type:Optional[str]=None, link_url:Optional[str]=None, campaign_id:Optional[int]=None) -> AdsCheckLinkResponse:
		"""Allows to check the ad link."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("ads.checkLink", **args)
		models = [AdsCheckLinkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def createAds(self, account_id:Optional[int]=None, data:Optional[str]=None) -> AdsCreateAdsResponse:
		"""Creates ads."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("ads.createAds", **args)
		models = [AdsCreateAdsResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def createCampaigns(self, account_id:Optional[int]=None, data:Optional[str]=None) -> AdsCreateCampaignsResponse:
		"""Creates advertising campaigns."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("ads.createCampaigns", **args)
		models = [AdsCreateCampaignsResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def createClients(self, account_id:Optional[int]=None, data:Optional[str]=None) -> AdsCreateClientsResponse:
		"""Creates clients of an advertising agency."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("ads.createClients", **args)
		models = [AdsCreateClientsResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def createTargetGroup(self, account_id:Optional[int]=None, client_id:Optional[int]=None, name:Optional[str]=None, lifetime:Optional[int]=None, target_pixel_id:Optional[int]=None, target_pixel_rules:Optional[str]=None) -> AdsCreateTargetGroupResponse:
		"""Creates a group to re-target ads for users who visited advertiser's site (viewed information about the product, registered, etc.)."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("ads.createTargetGroup", **args)
		models = [AdsCreateTargetGroupResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def deleteAds(self, account_id:Optional[int]=None, ids:Optional[str]=None) -> AdsDeleteAdsResponse:
		"""Archives ads."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("ads.deleteAds", **args)
		models = [AdsDeleteAdsResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def deleteCampaigns(self, account_id:Optional[int]=None, ids:Optional[str]=None) -> AdsDeleteCampaignsResponse:
		"""Archives advertising campaigns."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("ads.deleteCampaigns", **args)
		models = [AdsDeleteCampaignsResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def deleteClients(self, account_id:Optional[int]=None, ids:Optional[str]=None) -> AdsDeleteClientsResponse:
		"""Archives clients of an advertising agency."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("ads.deleteClients", **args)
		models = [AdsDeleteClientsResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def deleteTargetGroup(self, account_id:Optional[int]=None, client_id:Optional[int]=None, target_group_id:Optional[int]=None) -> BaseOkResponse:
		"""Deletes a retarget group."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("ads.deleteTargetGroup", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getAccounts(self) -> AdsGetAccountsResponse:
		"""Returns a list of advertising accounts."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("ads.getAccounts", **args)
		models = [AdsGetAccountsResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getAds(self, account_id:Optional[int]=None, ad_ids:Optional[str]=None, campaign_ids:Optional[str]=None, client_id:Optional[int]=None, include_deleted:Optional[bool]=None, only_deleted:Optional[bool]=None, limit:Optional[int]=None, offset:Optional[int]=None) -> AdsGetAdsResponse:
		"""Returns number of ads."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("ads.getAds", **args)
		models = [AdsGetAdsResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getAdsLayout(self, account_id:Optional[int]=None, client_id:Optional[int]=None, include_deleted:Optional[bool]=None, only_deleted:Optional[bool]=None, campaign_ids:Optional[str]=None, ad_ids:Optional[str]=None, limit:Optional[int]=None, offset:Optional[int]=None) -> AdsGetAdsLayoutResponse:
		"""Returns descriptions of ad layouts."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("ads.getAdsLayout", **args)
		models = [AdsGetAdsLayoutResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getAdsTargeting(self, account_id:Optional[int]=None, ad_ids:Optional[str]=None, campaign_ids:Optional[str]=None, client_id:Optional[int]=None, include_deleted:Optional[bool]=None, limit:Optional[int]=None, offset:Optional[int]=None) -> AdsGetAdsTargetingResponse:
		"""Returns ad targeting parameters."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("ads.getAdsTargeting", **args)
		models = [AdsGetAdsTargetingResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getBudget(self, account_id:Optional[int]=None) -> AdsGetBudgetResponse:
		"""Returns current budget of the advertising account."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("ads.getBudget", **args)
		models = [AdsGetBudgetResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getCampaigns(self, account_id:Optional[int]=None, client_id:Optional[int]=None, include_deleted:Optional[bool]=None, campaign_ids:Optional[str]=None, fields:Optional[list]=None) -> AdsGetCampaignsResponse:
		"""Returns a list of campaigns in an advertising account."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("ads.getCampaigns", **args)
		models = [AdsGetCampaignsResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getCategories(self, lang:Optional[str]=None) -> AdsGetCategoriesResponse:
		"""Returns a list of possible ad categories."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("ads.getCategories", **args)
		models = [AdsGetCategoriesResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getClients(self, account_id:Optional[int]=None) -> AdsGetClientsResponse:
		"""Returns a list of advertising agency's clients."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("ads.getClients", **args)
		models = [AdsGetClientsResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getDemographics(self, account_id:Optional[int]=None, ids_type:Optional[str]=None, ids:Optional[str]=None, period:Optional[str]=None, date_from:Optional[str]=None, date_to:Optional[str]=None) -> AdsGetDemographicsResponse:
		"""Returns demographics for ads or campaigns."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("ads.getDemographics", **args)
		models = [AdsGetDemographicsResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getFloodStats(self, account_id:Optional[int]=None) -> AdsGetFloodStatsResponse:
		"""Returns information about current state of a counter — number of remaining runs of methods and time to the next counter nulling in seconds."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("ads.getFloodStats", **args)
		models = [AdsGetFloodStatsResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getLookalikeRequests(self, account_id:Optional[int]=None, client_id:Optional[int]=None, requests_ids:Optional[str]=None, offset:Optional[int]=None, limit:Optional[int]=None, sort_by:Optional[str]=None) -> AdsGetLookalikeRequestsResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("ads.getLookalikeRequests", **args)
		models = [AdsGetLookalikeRequestsResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getMusicians(self, artist_name:Optional[str]=None) -> AdsGetMusiciansResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("ads.getMusicians", **args)
		models = [AdsGetMusiciansResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getMusiciansByIds(self, ids:Optional[list]=None) -> AdsGetMusiciansResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("ads.getMusiciansByIds", **args)
		models = [AdsGetMusiciansResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getOfficeUsers(self, account_id:Optional[int]=None) -> AdsGetOfficeUsersResponse:
		"""Returns a list of managers and supervisors of advertising account."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("ads.getOfficeUsers", **args)
		models = [AdsGetOfficeUsersResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getPostsReach(self, account_id:Optional[int]=None, ids_type:Optional[str]=None, ids:Optional[str]=None) -> AdsGetPostsReachResponse:
		"""Returns detailed statistics of promoted posts reach from campaigns and ads."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("ads.getPostsReach", **args)
		models = [AdsGetPostsReachResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getRejectionReason(self, account_id:Optional[int]=None, ad_id:Optional[int]=None) -> AdsGetRejectionReasonResponse:
		"""Returns a reason of ad rejection for pre-moderation."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("ads.getRejectionReason", **args)
		models = [AdsGetRejectionReasonResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getStatistics(self, account_id:Optional[int]=None, ids_type:Optional[str]=None, ids:Optional[str]=None, period:Optional[str]=None, date_from:Optional[str]=None, date_to:Optional[str]=None, stats_fields:Optional[list]=None) -> AdsGetStatisticsResponse:
		"""Returns statistics of performance indicators for ads, campaigns, clients or the whole account."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("ads.getStatistics", **args)
		models = [AdsGetStatisticsResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getSuggestions(self, section:Optional[str]=None, ids:Optional[str]=None, q:Optional[str]=None, country:Optional[int]=None, cities:Optional[str]=None, lang:Optional[str]=None) -> AdsGetSuggestionsResponse| AdsGetSuggestionsRegionsResponse| AdsGetSuggestionsCitiesResponse| AdsGetSuggestionsSchoolsResponse:
		"""Returns a set of auto-suggestions for various targeting parameters."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("ads.getSuggestions", **args)
		models = [AdsGetSuggestionsResponse, AdsGetSuggestionsRegionsResponse, AdsGetSuggestionsCitiesResponse, AdsGetSuggestionsSchoolsResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getTargetGroups(self, account_id:Optional[int]=None, client_id:Optional[int]=None, extended:Optional[bool]=None) -> AdsGetTargetGroupsResponse:
		"""Returns a list of target groups."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("ads.getTargetGroups", **args)
		models = [AdsGetTargetGroupsResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getTargetingStats(self, account_id:Optional[int]=None, client_id:Optional[int]=None, criteria:Optional[str]=None, ad_id:Optional[int]=None, ad_format:Optional[int]=None, ad_platform:Optional[str]=None, ad_platform_no_wall:Optional[str]=None, ad_platform_no_ad_network:Optional[str]=None, publisher_platforms:Optional[str]=None, link_url:Optional[str]=None, link_domain:Optional[str]=None, need_precise:Optional[bool]=None, impressions_limit_period:Optional[int]=None) -> AdsGetTargetingStatsResponse:
		"""Returns the size of targeting audience, and also recommended values for CPC and CPM."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("ads.getTargetingStats", **args)
		models = [AdsGetTargetingStatsResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getUploadURL(self, ad_format:Optional[int]=None, icon:Optional[int]=None) -> AdsGetUploadURLResponse:
		"""Returns URL to upload an ad photo to."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("ads.getUploadURL", **args)
		models = [AdsGetUploadURLResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getVideoUploadURL(self) -> AdsGetVideoUploadURLResponse:
		"""Returns URL to upload an ad video to."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("ads.getVideoUploadURL", **args)
		models = [AdsGetVideoUploadURLResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def importTargetContacts(self, account_id:Optional[int]=None, client_id:Optional[int]=None, target_group_id:Optional[int]=None, contacts:Optional[str]=None) -> AdsImportTargetContactsResponse:
		"""Imports a list of advertiser's contacts to count VK registered users against the target group."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("ads.importTargetContacts", **args)
		models = [AdsImportTargetContactsResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def removeOfficeUsers(self, account_id:Optional[int]=None, ids:Optional[str]=None) -> AdsRemoveOfficeUsersResponse:
		"""Removes managers and/or supervisors from advertising account."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("ads.removeOfficeUsers", **args)
		models = [AdsRemoveOfficeUsersResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def updateAds(self, account_id:Optional[int]=None, data:Optional[str]=None) -> AdsUpdateAdsResponse:
		"""Edits ads."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("ads.updateAds", **args)
		models = [AdsUpdateAdsResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def updateCampaigns(self, account_id:Optional[int]=None, data:Optional[str]=None) -> AdsUpdateCampaignsResponse:
		"""Edits advertising campaigns."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("ads.updateCampaigns", **args)
		models = [AdsUpdateCampaignsResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def updateClients(self, account_id:Optional[int]=None, data:Optional[str]=None) -> AdsUpdateClientsResponse:
		"""Edits clients of an advertising agency."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("ads.updateClients", **args)
		models = [AdsUpdateClientsResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def updateOfficeUsers(self, account_id:Optional[int]=None, data:Optional[str]=None) -> AdsUpdateOfficeUsersResponse:
		"""Adds managers and/or supervisors to advertising account."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("ads.updateOfficeUsers", **args)
		models = [AdsUpdateOfficeUsersResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def updateTargetGroup(self, account_id:Optional[int]=None, client_id:Optional[int]=None, target_group_id:Optional[int]=None, name:Optional[str]=None, domain:Optional[str]=None, lifetime:Optional[int]=None, target_pixel_id:Optional[int]=None, target_pixel_rules:Optional[str]=None) -> BaseOkResponse:
		"""Edits a retarget group."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("ads.updateTargetGroup", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)



class Adsweb(BaseMethod):
	def __init__(self, vk):
		super().__init__(vk)

	async def getAdCategories(self, office_id:Optional[int]=None) -> AdswebGetAdCategoriesResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("adsweb.getAdCategories", **args)
		models = [AdswebGetAdCategoriesResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getAdUnitCode(self) -> AdswebGetAdUnitCodeResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("adsweb.getAdUnitCode", **args)
		models = [AdswebGetAdUnitCodeResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getAdUnits(self, office_id:Optional[int]=None, sites_ids:Optional[str]=None, ad_units_ids:Optional[str]=None, fields:Optional[str]=None, limit:Optional[int]=None, offset:Optional[int]=None) -> AdswebGetAdUnitsResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("adsweb.getAdUnits", **args)
		models = [AdswebGetAdUnitsResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getFraudHistory(self, office_id:Optional[int]=None, sites_ids:Optional[str]=None, limit:Optional[int]=None, offset:Optional[int]=None) -> AdswebGetFraudHistoryResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("adsweb.getFraudHistory", **args)
		models = [AdswebGetFraudHistoryResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getSites(self, office_id:Optional[int]=None, sites_ids:Optional[str]=None, fields:Optional[str]=None, limit:Optional[int]=None, offset:Optional[int]=None) -> AdswebGetSitesResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("adsweb.getSites", **args)
		models = [AdswebGetSitesResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getStatistics(self, office_id:Optional[int]=None, ids_type:Optional[str]=None, ids:Optional[str]=None, period:Optional[str]=None, date_from:Optional[str]=None, date_to:Optional[str]=None, fields:Optional[str]=None, limit:Optional[int]=None, page_id:Optional[str]=None) -> AdswebGetStatisticsResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("adsweb.getStatistics", **args)
		models = [AdswebGetStatisticsResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)



class Appwidgets(BaseMethod):
	def __init__(self, vk):
		super().__init__(vk)

	async def getAppImageUploadServer(self, image_type:Optional[str]=None) -> AppWidgetsGetAppImageUploadServerResponse:
		"""Returns a URL for uploading a photo to the community collection for community app widgets"""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("appwidgets.getAppImageUploadServer", **args)
		models = [AppWidgetsGetAppImageUploadServerResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getAppImages(self, offset:Optional[int]=None, count:Optional[int]=None, image_type:Optional[str]=None) -> AppWidgetsGetAppImagesResponse:
		"""Returns an app collection of images for community app widgets"""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("appwidgets.getAppImages", **args)
		models = [AppWidgetsGetAppImagesResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getGroupImageUploadServer(self, image_type:Optional[str]=None) -> AppWidgetsGetGroupImageUploadServerResponse:
		"""Returns a URL for uploading a photo to the community collection for community app widgets"""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("appwidgets.getGroupImageUploadServer", **args)
		models = [AppWidgetsGetGroupImageUploadServerResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getGroupImages(self, offset:Optional[int]=None, count:Optional[int]=None, image_type:Optional[str]=None) -> AppWidgetsGetGroupImagesResponse:
		"""Returns a community collection of images for community app widgets"""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("appwidgets.getGroupImages", **args)
		models = [AppWidgetsGetGroupImagesResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getImagesById(self, images:Optional[list]=None) -> AppWidgetsGetImagesByIdResponse:
		"""Returns an image for community app widgets by its ID"""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("appwidgets.getImagesById", **args)
		models = [AppWidgetsGetImagesByIdResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def saveAppImage(self, hash:Optional[str]=None, image:Optional[str]=None) -> AppWidgetsSaveAppImageResponse:
		"""Allows to save image into app collection for community app widgets"""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("appwidgets.saveAppImage", **args)
		models = [AppWidgetsSaveAppImageResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def saveGroupImage(self, hash:Optional[str]=None, image:Optional[str]=None) -> AppWidgetsSaveGroupImageResponse:
		"""Allows to save image into community collection for community app widgets"""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("appwidgets.saveGroupImage", **args)
		models = [AppWidgetsSaveGroupImageResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def update(self, code:Optional[str]=None, type:Optional[str]=None) -> BaseOkResponse:
		"""Allows to update community app widget"""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("appwidgets.update", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)



class Apps(BaseMethod):
	def __init__(self, vk):
		super().__init__(vk)

	async def deleteAppRequests(self) -> BaseOkResponse:
		"""Deletes all request notifications from the current app."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("apps.deleteAppRequests", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def get(self, app_id:Optional[int]=None, app_ids:Optional[list]=None, platform:Optional[str]=None, extended:Optional[bool]=None, return_friends:Optional[bool]=None, fields:Optional[list]=None, name_case:Optional[str]=None) -> AppsGetResponse:
		"""Returns applications data."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("apps.get", **args)
		models = [AppsGetResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getCatalog(self, sort:Optional[str]=None, offset:Optional[int]=None, count:Optional[int]=None, platform:Optional[str]=None, extended:Optional[bool]=None, return_friends:Optional[bool]=None, fields:Optional[list]=None, name_case:Optional[str]=None, q:Optional[str]=None, genre_id:Optional[int]=None, filter:Optional[str]=None) -> AppsGetCatalogResponse:
		"""Returns a list of applications (apps) available to users in the App Catalog."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("apps.getCatalog", **args)
		models = [AppsGetCatalogResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getFriendsList(self, extended:Optional[bool]=None, count:Optional[int]=None, offset:Optional[int]=None, type:Optional[str]=None, fields:Optional[list]=None) -> AppsGetFriendsListResponse| AppsGetFriendsListExtendedResponse:
		"""Creates friends list for requests and invites in current app."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("apps.getFriendsList", **args)
		models = [AppsGetFriendsListResponse, AppsGetFriendsListExtendedResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getLeaderboard(self, type:Optional[str]=None, _global:Optional[bool]=None, extended:Optional[bool]=None) -> AppsGetLeaderboardResponse| AppsGetLeaderboardExtendedResponse:
		"""Returns players rating in the game."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("apps.getLeaderboard", **args)
		models = [AppsGetLeaderboardResponse, AppsGetLeaderboardExtendedResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getMiniAppPolicies(self, app_id:Optional[int]=None) -> AppsGetMiniAppPoliciesResponse:
		"""Returns policies and terms given to a mini app."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("apps.getMiniAppPolicies", **args)
		models = [AppsGetMiniAppPoliciesResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getScopes(self, type:Optional[str]=None) -> AppsGetScopesResponse:
		"""Returns scopes for auth"""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("apps.getScopes", **args)
		models = [AppsGetScopesResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getScore(self, user_id:Optional[int]=None) -> AppsGetScoreResponse:
		"""Returns user score in app"""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("apps.getScore", **args)
		models = [AppsGetScoreResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def promoHasActiveGift(self, promo_id:Optional[int]=None, user_id:Optional[int]=None) -> BaseBoolResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("apps.promoHasActiveGift", **args)
		models = [BaseBoolResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def promoUseGift(self, promo_id:Optional[int]=None, user_id:Optional[int]=None) -> BaseBoolResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("apps.promoUseGift", **args)
		models = [BaseBoolResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def sendRequest(self, user_id:Optional[int]=None, text:Optional[str]=None, type:Optional[str]=None, name:Optional[str]=None, key:Optional[str]=None, separate:Optional[bool]=None) -> AppsSendRequestResponse:
		"""Sends a request to another user in an app that uses VK authorization."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("apps.sendRequest", **args)
		models = [AppsSendRequestResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)



class Auth(BaseMethod):
	def __init__(self, vk):
		super().__init__(vk)

	async def restore(self, phone:Optional[str]=None, last_name:Optional[str]=None) -> AuthRestoreResponse:
		"""Allows to restore account access using a code received via SMS. ' This method is only available for apps with [vk.com/dev/auth_direct|Direct authorization] access. '"""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("auth.restore", **args)
		models = [AuthRestoreResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)



class Board(BaseMethod):
	def __init__(self, vk):
		super().__init__(vk)

	async def addTopic(self, group_id:Optional[int]=None, title:Optional[str]=None, text:Optional[str]=None, from_group:Optional[bool]=None, attachments:Optional[str]=None) -> BoardAddTopicResponse:
		"""Creates a new topic on a community's discussion board."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("board.addTopic", **args)
		models = [BoardAddTopicResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def closeTopic(self, group_id:Optional[int]=None, topic_id:Optional[int]=None) -> BaseOkResponse:
		"""Closes a topic on a community's discussion board so that comments cannot be posted."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("board.closeTopic", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def createComment(self, group_id:Optional[int]=None, topic_id:Optional[int]=None, message:Optional[str]=None, attachments:Optional[str]=None, from_group:Optional[bool]=None, sticker_id:Optional[int]=None, guid:Optional[str]=None) -> BoardCreateCommentResponse:
		"""Adds a comment on a topic on a community's discussion board."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("board.createComment", **args)
		models = [BoardCreateCommentResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def deleteComment(self, group_id:Optional[int]=None, topic_id:Optional[int]=None, comment_id:Optional[int]=None) -> BaseOkResponse:
		"""Deletes a comment on a topic on a community's discussion board."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("board.deleteComment", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def deleteTopic(self, group_id:Optional[int]=None, topic_id:Optional[int]=None) -> BaseOkResponse:
		"""Deletes a topic from a community's discussion board."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("board.deleteTopic", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def editComment(self, group_id:Optional[int]=None, topic_id:Optional[int]=None, comment_id:Optional[int]=None, message:Optional[str]=None, attachments:Optional[str]=None) -> BaseOkResponse:
		"""Edits a comment on a topic on a community's discussion board."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("board.editComment", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def editTopic(self, group_id:Optional[int]=None, topic_id:Optional[int]=None, title:Optional[str]=None) -> BaseOkResponse:
		"""Edits the title of a topic on a community's discussion board."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("board.editTopic", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def fixTopic(self, group_id:Optional[int]=None, topic_id:Optional[int]=None) -> BaseOkResponse:
		"""Pins a topic (fixes its place) to the top of a community's discussion board."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("board.fixTopic", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getComments(self, group_id:Optional[int]=None, topic_id:Optional[int]=None, need_likes:Optional[bool]=None, start_comment_id:Optional[int]=None, offset:Optional[int]=None, count:Optional[int]=None, extended:Optional[bool]=None, sort:Optional[str]=None) -> BoardGetCommentsResponse| BoardGetCommentsExtendedResponse:
		"""Returns a list of comments on a topic on a community's discussion board."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("board.getComments", **args)
		models = [BoardGetCommentsResponse, BoardGetCommentsExtendedResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getTopics(self, group_id:Optional[int]=None, topic_ids:Optional[list]=None, order:Optional[int]=None, offset:Optional[int]=None, count:Optional[int]=None, extended:Optional[bool]=None, preview:Optional[int]=None, preview_length:Optional[int]=None) -> BoardGetTopicsResponse| BoardGetTopicsExtendedResponse:
		"""Returns a list of topics on a community's discussion board."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("board.getTopics", **args)
		models = [BoardGetTopicsResponse, BoardGetTopicsExtendedResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def openTopic(self, group_id:Optional[int]=None, topic_id:Optional[int]=None) -> BaseOkResponse:
		"""Re-opens a previously closed topic on a community's discussion board."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("board.openTopic", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def restoreComment(self, group_id:Optional[int]=None, topic_id:Optional[int]=None, comment_id:Optional[int]=None) -> BaseOkResponse:
		"""Restores a comment deleted from a topic on a community's discussion board."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("board.restoreComment", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def unfixTopic(self, group_id:Optional[int]=None, topic_id:Optional[int]=None) -> BaseOkResponse:
		"""Unpins a pinned topic from the top of a community's discussion board."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("board.unfixTopic", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)



class Database(BaseMethod):
	def __init__(self, vk):
		super().__init__(vk)

	async def getChairs(self, faculty_id:Optional[int]=None, offset:Optional[int]=None, count:Optional[int]=None) -> DatabaseGetChairsResponse:
		"""Returns list of chairs on a specified faculty."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("database.getChairs", **args)
		models = [DatabaseGetChairsResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getCities(self, country_id:Optional[int]=None, region_id:Optional[int]=None, q:Optional[str]=None, need_all:Optional[bool]=None, offset:Optional[int]=None, count:Optional[int]=None) -> DatabaseGetCitiesResponse:
		"""Returns a list of cities."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("database.getCities", **args)
		models = [DatabaseGetCitiesResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getCitiesById(self, city_ids:Optional[list]=None) -> DatabaseGetCitiesByIdResponse:
		"""Returns information about cities by their IDs."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("database.getCitiesById", **args)
		models = [DatabaseGetCitiesByIdResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getCountries(self, need_all:Optional[bool]=None, code:Optional[str]=None, offset:Optional[int]=None, count:Optional[int]=None) -> DatabaseGetCountriesResponse:
		"""Returns a list of countries."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("database.getCountries", **args)
		models = [DatabaseGetCountriesResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getCountriesById(self, country_ids:Optional[list]=None) -> DatabaseGetCountriesByIdResponse:
		"""Returns information about countries by their IDs."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("database.getCountriesById", **args)
		models = [DatabaseGetCountriesByIdResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getFaculties(self, university_id:Optional[int]=None, offset:Optional[int]=None, count:Optional[int]=None) -> DatabaseGetFacultiesResponse:
		"""Returns a list of faculties (i.e., university departments)."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("database.getFaculties", **args)
		models = [DatabaseGetFacultiesResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getMetroStations(self, city_id:Optional[int]=None, offset:Optional[int]=None, count:Optional[int]=None, extended:Optional[bool]=None) -> DatabaseGetMetroStationsResponse:
		"""Get metro stations by city"""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("database.getMetroStations", **args)
		models = [DatabaseGetMetroStationsResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getMetroStationsById(self, station_ids:Optional[list]=None) -> DatabaseGetMetroStationsByIdResponse:
		"""Get metro station by his id"""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("database.getMetroStationsById", **args)
		models = [DatabaseGetMetroStationsByIdResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getRegions(self, country_id:Optional[int]=None, q:Optional[str]=None, offset:Optional[int]=None, count:Optional[int]=None) -> DatabaseGetRegionsResponse:
		"""Returns a list of regions."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("database.getRegions", **args)
		models = [DatabaseGetRegionsResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getSchoolClasses(self, country_id:Optional[int]=None) -> DatabaseGetSchoolClassesResponse:
		"""Returns a list of school classes specified for the country."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("database.getSchoolClasses", **args)
		models = [DatabaseGetSchoolClassesResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getSchools(self, q:Optional[str]=None, city_id:Optional[int]=None, offset:Optional[int]=None, count:Optional[int]=None) -> DatabaseGetSchoolsResponse:
		"""Returns a list of schools."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("database.getSchools", **args)
		models = [DatabaseGetSchoolsResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getUniversities(self, q:Optional[str]=None, country_id:Optional[int]=None, city_id:Optional[int]=None, offset:Optional[int]=None, count:Optional[int]=None) -> DatabaseGetUniversitiesResponse:
		"""Returns a list of higher education institutions."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("database.getUniversities", **args)
		models = [DatabaseGetUniversitiesResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)



class Docs(BaseMethod):
	def __init__(self, vk):
		super().__init__(vk)

	async def add(self, owner_id:Optional[int]=None, doc_id:Optional[int]=None, access_key:Optional[str]=None) -> DocsAddResponse:
		"""Copies a document to a user's or community's document list."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("docs.add", **args)
		models = [DocsAddResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def delete(self, owner_id:Optional[int]=None, doc_id:Optional[int]=None) -> BaseOkResponse:
		"""Deletes a user or community document."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("docs.delete", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def edit(self, owner_id:Optional[int]=None, doc_id:Optional[int]=None, title:Optional[str]=None, tags:Optional[list]=None) -> BaseOkResponse:
		"""Edits a document."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("docs.edit", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def get(self, count:Optional[int]=None, offset:Optional[int]=None, type:Optional[int]=None, owner_id:Optional[int]=None, return_tags:Optional[bool]=None) -> DocsGetResponse:
		"""Returns detailed information about user or community documents."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("docs.get", **args)
		models = [DocsGetResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getById(self, docs:Optional[list]=None, return_tags:Optional[bool]=None) -> DocsGetByIdResponse:
		"""Returns information about documents by their IDs."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("docs.getById", **args)
		models = [DocsGetByIdResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getMessagesUploadServer(self, type:Optional[str]=None, peer_id:Optional[int]=None) -> DocsGetUploadServerResponse:
		"""Returns the server address for document upload."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("docs.getMessagesUploadServer", **args)
		models = [DocsGetUploadServerResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getTypes(self, owner_id:Optional[int]=None) -> DocsGetTypesResponse:
		"""Returns documents types available for current user."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("docs.getTypes", **args)
		models = [DocsGetTypesResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getUploadServer(self, group_id:Optional[int]=None) -> DocsGetUploadServerResponse:
		"""Returns the server address for document upload."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("docs.getUploadServer", **args)
		models = [DocsGetUploadServerResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getWallUploadServer(self, group_id:Optional[int]=None) -> BaseGetUploadServerResponse:
		"""Returns the server address for document upload onto a user's or community's wall."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("docs.getWallUploadServer", **args)
		models = [BaseGetUploadServerResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def save(self, file:Optional[str]=None, title:Optional[str]=None, tags:Optional[str]=None, return_tags:Optional[bool]=None) -> DocsSaveResponse:
		"""Saves a document after [vk.com/dev/upload_files_2|uploading it to a server]."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("docs.save", **args)
		models = [DocsSaveResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def search(self, q:Optional[str]=None, search_own:Optional[bool]=None, count:Optional[int]=None, offset:Optional[int]=None, return_tags:Optional[bool]=None) -> DocsSearchResponse:
		"""Returns a list of documents matching the search criteria."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("docs.search", **args)
		models = [DocsSearchResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)



class Donut(BaseMethod):
	def __init__(self, vk):
		super().__init__(vk)

	async def getFriends(self, owner_id:Optional[int]=None, offset:Optional[int]=None, count:Optional[int]=None, fields:Optional[list]=None) -> GroupsGetMembersFieldsResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("donut.getFriends", **args)
		models = [GroupsGetMembersFieldsResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getSubscription(self, owner_id:Optional[int]=None) -> DonutGetSubscriptionResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("donut.getSubscription", **args)
		models = [DonutGetSubscriptionResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getSubscriptions(self, fields:Optional[list]=None, offset:Optional[int]=None, count:Optional[int]=None) -> DonutGetSubscriptionsResponse:
		"""Returns a list of user's VK Donut subscriptions."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("donut.getSubscriptions", **args)
		models = [DonutGetSubscriptionsResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def isDon(self, owner_id:Optional[int]=None) -> BaseBoolResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("donut.isDon", **args)
		models = [BaseBoolResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)



class Downloadedgames(BaseMethod):
	def __init__(self, vk):
		super().__init__(vk)

	async def getPaidStatus(self, user_id:Optional[int]=None) -> DownloadedGamesPaidStatusResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("downloadedgames.getPaidStatus", **args)
		models = [DownloadedGamesPaidStatusResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)



class Fave(BaseMethod):
	def __init__(self, vk):
		super().__init__(vk)

	async def addArticle(self, url:Optional[str]=None) -> BaseOkResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("fave.addArticle", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def addLink(self, link:Optional[str]=None) -> BaseOkResponse:
		"""Adds a link to user faves."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("fave.addLink", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def addPage(self, user_id:Optional[int]=None, group_id:Optional[int]=None) -> BaseOkResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("fave.addPage", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def addPost(self, owner_id:Optional[int]=None, id:Optional[int]=None, access_key:Optional[str]=None) -> BaseOkResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("fave.addPost", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def addProduct(self, owner_id:Optional[int]=None, id:Optional[int]=None, access_key:Optional[str]=None) -> BaseOkResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("fave.addProduct", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def addTag(self, name:Optional[str]=None, position:Optional[str]=None) -> FaveAddTagResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("fave.addTag", **args)
		models = [FaveAddTagResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def addVideo(self, owner_id:Optional[int]=None, id:Optional[int]=None, access_key:Optional[str]=None) -> BaseOkResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("fave.addVideo", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def editTag(self, id:Optional[int]=None, name:Optional[str]=None) -> BaseOkResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("fave.editTag", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def get(self, extended:Optional[bool]=None, item_type:Optional[str]=None, tag_id:Optional[int]=None, offset:Optional[int]=None, count:Optional[int]=None, fields:Optional[str]=None, is_from_snackbar:Optional[bool]=None) -> FaveGetResponse| FaveGetExtendedResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("fave.get", **args)
		models = [FaveGetResponse, FaveGetExtendedResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getPages(self, offset:Optional[int]=None, count:Optional[int]=None, type:Optional[str]=None, fields:Optional[list]=None, tag_id:Optional[int]=None) -> FaveGetPagesResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("fave.getPages", **args)
		models = [FaveGetPagesResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getTags(self) -> FaveGetTagsResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("fave.getTags", **args)
		models = [FaveGetTagsResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def markSeen(self) -> BaseBoolResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("fave.markSeen", **args)
		models = [BaseBoolResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def removeArticle(self, owner_id:Optional[int]=None, article_id:Optional[int]=None) -> BaseBoolResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("fave.removeArticle", **args)
		models = [BaseBoolResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def removeLink(self, link_id:Optional[str]=None, link:Optional[str]=None) -> BaseOkResponse:
		"""Removes link from the user's faves."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("fave.removeLink", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def removePage(self, user_id:Optional[int]=None, group_id:Optional[int]=None) -> BaseOkResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("fave.removePage", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def removePost(self, owner_id:Optional[int]=None, id:Optional[int]=None) -> BaseOkResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("fave.removePost", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def removeProduct(self, owner_id:Optional[int]=None, id:Optional[int]=None) -> BaseOkResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("fave.removeProduct", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def removeTag(self, id:Optional[int]=None) -> BaseOkResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("fave.removeTag", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def removeVideo(self, owner_id:Optional[int]=None, id:Optional[int]=None) -> BaseOkResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("fave.removeVideo", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def reorderTags(self, ids:Optional[list]=None) -> BaseOkResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("fave.reorderTags", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def setPageTags(self, user_id:Optional[int]=None, group_id:Optional[int]=None, tag_ids:Optional[list]=None) -> BaseOkResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("fave.setPageTags", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def setTags(self, item_type:Optional[str]=None, item_owner_id:Optional[int]=None, item_id:Optional[int]=None, tag_ids:Optional[list]=None, link_id:Optional[str]=None, link_url:Optional[str]=None) -> BaseOkResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("fave.setTags", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def trackPageInteraction(self, user_id:Optional[int]=None, group_id:Optional[int]=None) -> BaseOkResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("fave.trackPageInteraction", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)



class Friends(BaseMethod):
	def __init__(self, vk):
		super().__init__(vk)

	async def add(self, user_id:Optional[int]=None, text:Optional[str]=None, follow:Optional[bool]=None) -> FriendsAddResponse:
		"""Approves or creates a friend request."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("friends.add", **args)
		models = [FriendsAddResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def addList(self, name:Optional[str]=None, user_ids:Optional[list]=None) -> FriendsAddListResponse:
		"""Creates a new friend list for the current user."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("friends.addList", **args)
		models = [FriendsAddListResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def areFriends(self, user_ids:Optional[list]=None, need_sign:Optional[bool]=None, extended:Optional[bool]=None) -> FriendsAreFriendsResponse| FriendsAreFriendsExtendedResponse:
		"""Checks the current user's friendship status with other specified users."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("friends.areFriends", **args)
		models = [FriendsAreFriendsResponse, FriendsAreFriendsExtendedResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def delete(self, user_id:Optional[int]=None) -> FriendsDeleteResponse:
		"""Declines a friend request or deletes a user from the current user's friend list."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("friends.delete", **args)
		models = [FriendsDeleteResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def deleteAllRequests(self) -> BaseOkResponse:
		"""Marks all incoming friend requests as viewed."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("friends.deleteAllRequests", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def deleteList(self, list_id:Optional[int]=None) -> BaseOkResponse:
		"""Deletes a friend list of the current user."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("friends.deleteList", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def edit(self, user_id:Optional[int]=None, list_ids:Optional[list]=None) -> BaseOkResponse:
		"""Edits the friend lists of the selected user."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("friends.edit", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def editList(self, name:Optional[str]=None, list_id:Optional[int]=None, user_ids:Optional[list]=None, add_user_ids:Optional[list]=None, delete_user_ids:Optional[list]=None) -> BaseOkResponse:
		"""Edits a friend list of the current user."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("friends.editList", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def get(self, user_id:Optional[int]=None, order:Optional[str]=None, list_id:Optional[int]=None, count:Optional[int]=None, offset:Optional[int]=None, fields:Optional[list]=None, name_case:Optional[str]=None, ref:Optional[str]=None) -> FriendsGetResponse| FriendsGetFieldsResponse:
		"""Returns a list of user IDs or detailed information about a user's friends."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("friends.get", **args)
		models = [FriendsGetResponse, FriendsGetFieldsResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getAppUsers(self) -> FriendsGetAppUsersResponse:
		"""Returns a list of IDs of the current user's friends who installed the application."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("friends.getAppUsers", **args)
		models = [FriendsGetAppUsersResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getByPhones(self, phones:Optional[list]=None, fields:Optional[list]=None) -> FriendsGetByPhonesResponse:
		"""Returns a list of the current user's friends whose phone numbers, validated or specified in a profile, are in a given list."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("friends.getByPhones", **args)
		models = [FriendsGetByPhonesResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getLists(self, user_id:Optional[int]=None, return_system:Optional[bool]=None) -> FriendsGetListsResponse:
		"""Returns a list of the user's friend lists."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("friends.getLists", **args)
		models = [FriendsGetListsResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getMutual(self, source_uid:Optional[int]=None, target_uid:Optional[int]=None, target_uids:Optional[list]=None, order:Optional[str]=None, count:Optional[int]=None, offset:Optional[int]=None) -> FriendsGetMutualResponse| FriendsGetMutualTargetUidsResponse:
		"""Returns a list of user IDs of the mutual friends of two users."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("friends.getMutual", **args)
		models = [FriendsGetMutualResponse, FriendsGetMutualTargetUidsResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getOnline(self, user_id:Optional[int]=None, list_id:Optional[int]=None, online_mobile:Optional[bool]=None, order:Optional[str]=None, count:Optional[int]=None, offset:Optional[int]=None) -> FriendsGetOnlineResponse| FriendsGetOnlineOnlineMobileResponse:
		"""Returns a list of user IDs of a user's friends who are online."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("friends.getOnline", **args)
		models = [FriendsGetOnlineResponse, FriendsGetOnlineOnlineMobileResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getRecent(self, count:Optional[int]=None) -> FriendsGetRecentResponse:
		"""Returns a list of user IDs of the current user's recently added friends."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("friends.getRecent", **args)
		models = [FriendsGetRecentResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getRequests(self, offset:Optional[int]=None, count:Optional[int]=None, extended:Optional[bool]=None, need_mutual:Optional[bool]=None, out:Optional[bool]=None, sort:Optional[int]=None, need_viewed:Optional[bool]=None, suggested:Optional[bool]=None, ref:Optional[str]=None, fields:Optional[list]=None) -> FriendsGetRequestsResponse| FriendsGetRequestsNeedMutualResponse| FriendsGetRequestsExtendedResponse:
		"""Returns information about the current user's incoming and outgoing friend requests."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("friends.getRequests", **args)
		models = [FriendsGetRequestsResponse, FriendsGetRequestsNeedMutualResponse, FriendsGetRequestsExtendedResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getSuggestions(self, filter:Optional[list]=None, count:Optional[int]=None, offset:Optional[int]=None, fields:Optional[list]=None, name_case:Optional[str]=None) -> FriendsGetSuggestionsResponse:
		"""Returns a list of profiles of users whom the current user may know."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("friends.getSuggestions", **args)
		models = [FriendsGetSuggestionsResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def search(self, user_id:Optional[int]=None, q:Optional[str]=None, fields:Optional[list]=None, name_case:Optional[str]=None, offset:Optional[int]=None, count:Optional[int]=None) -> FriendsSearchResponse:
		"""Returns a list of friends matching the search criteria."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("friends.search", **args)
		models = [FriendsSearchResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)



class Gifts(BaseMethod):
	def __init__(self, vk):
		super().__init__(vk)

	async def get(self, user_id:Optional[int]=None, count:Optional[int]=None, offset:Optional[int]=None) -> GiftsGetResponse:
		"""Returns a list of user gifts."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("gifts.get", **args)
		models = [GiftsGetResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)



class Groups(BaseMethod):
	def __init__(self, vk):
		super().__init__(vk)

	async def addAddress(self, group_id:Optional[int]=None, title:Optional[str]=None, address:Optional[str]=None, additional_address:Optional[str]=None, country_id:Optional[int]=None, city_id:Optional[int]=None, metro_id:Optional[int]=None, latitude:Optional[int]=None, longitude:Optional[int]=None, phone:Optional[str]=None, work_info_status:Optional[str]=None, timetable:Optional[str]=None, is_main_address:Optional[bool]=None) -> GroupsAddAddressResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("groups.addAddress", **args)
		models = [GroupsAddAddressResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def addCallbackServer(self, group_id:Optional[int]=None, url:Optional[str]=None, title:Optional[str]=None, secret_key:Optional[str]=None) -> GroupsAddCallbackServerResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("groups.addCallbackServer", **args)
		models = [GroupsAddCallbackServerResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def addLink(self, group_id:Optional[int]=None, link:Optional[str]=None, text:Optional[str]=None) -> GroupsAddLinkResponse:
		"""Allows to add a link to the community."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("groups.addLink", **args)
		models = [GroupsAddLinkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def approveRequest(self, group_id:Optional[int]=None, user_id:Optional[int]=None) -> BaseOkResponse:
		"""Allows to approve join request to the community."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("groups.approveRequest", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def ban(self, group_id:Optional[int]=None, owner_id:Optional[int]=None, end_date:Optional[int]=None, reason:Optional[int]=None, comment:Optional[str]=None, comment_visible:Optional[bool]=None) -> BaseOkResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("groups.ban", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def create(self, title:Optional[str]=None, description:Optional[str]=None, type:Optional[str]=None, public_category:Optional[int]=None, public_subcategory:Optional[int]=None, subtype:Optional[int]=None) -> GroupsCreateResponse:
		"""Creates a new community."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("groups.create", **args)
		models = [GroupsCreateResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def deleteAddress(self, group_id:Optional[int]=None, address_id:Optional[int]=None) -> BaseOkResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("groups.deleteAddress", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def deleteCallbackServer(self, group_id:Optional[int]=None, server_id:Optional[int]=None) -> BaseOkResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("groups.deleteCallbackServer", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def deleteLink(self, group_id:Optional[int]=None, link_id:Optional[int]=None) -> BaseOkResponse:
		"""Allows to delete a link from the community."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("groups.deleteLink", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def disableOnline(self, group_id:Optional[int]=None) -> BaseOkResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("groups.disableOnline", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def edit(self, group_id:Optional[int]=None, title:Optional[str]=None, description:Optional[str]=None, screen_name:Optional[str]=None, access:Optional[int]=None, website:Optional[str]=None, subject:Optional[str]=None, email:Optional[str]=None, phone:Optional[str]=None, rss:Optional[str]=None, event_start_date:Optional[int]=None, event_finish_date:Optional[int]=None, event_group_id:Optional[int]=None, public_category:Optional[int]=None, public_subcategory:Optional[int]=None, public_date:Optional[str]=None, wall:Optional[int]=None, topics:Optional[int]=None, photos:Optional[int]=None, video:Optional[int]=None, audio:Optional[int]=None, links:Optional[bool]=None, events:Optional[bool]=None, places:Optional[bool]=None, contacts:Optional[bool]=None, docs:Optional[int]=None, wiki:Optional[int]=None, messages:Optional[bool]=None, articles:Optional[bool]=None, addresses:Optional[bool]=None, age_limits:Optional[int]=None, market:Optional[bool]=None, market_comments:Optional[bool]=None, market_country:Optional[list]=None, market_city:Optional[list]=None, market_currency:Optional[int]=None, market_contact:Optional[int]=None, market_wiki:Optional[int]=None, obscene_filter:Optional[bool]=None, obscene_stopwords:Optional[bool]=None, obscene_words:Optional[list]=None, main_section:Optional[int]=None, secondary_section:Optional[int]=None, country:Optional[int]=None, city:Optional[int]=None) -> BaseOkResponse:
		"""Edits a community."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("groups.edit", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def editAddress(self, group_id:Optional[int]=None, address_id:Optional[int]=None, title:Optional[str]=None, address:Optional[str]=None, additional_address:Optional[str]=None, country_id:Optional[int]=None, city_id:Optional[int]=None, metro_id:Optional[int]=None, latitude:Optional[int]=None, longitude:Optional[int]=None, phone:Optional[str]=None, work_info_status:Optional[str]=None, timetable:Optional[str]=None, is_main_address:Optional[bool]=None) -> GroupsEditAddressResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("groups.editAddress", **args)
		models = [GroupsEditAddressResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def editCallbackServer(self, group_id:Optional[int]=None, server_id:Optional[int]=None, url:Optional[str]=None, title:Optional[str]=None, secret_key:Optional[str]=None) -> BaseOkResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("groups.editCallbackServer", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def editLink(self, group_id:Optional[int]=None, link_id:Optional[int]=None, text:Optional[str]=None) -> BaseOkResponse:
		"""Allows to edit a link in the community."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("groups.editLink", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def editManager(self, group_id:Optional[int]=None, user_id:Optional[int]=None, role:Optional[str]=None, is_contact:Optional[bool]=None, contact_position:Optional[str]=None, contact_phone:Optional[str]=None, contact_email:Optional[str]=None) -> BaseOkResponse:
		"""Allows to add, remove or edit the community manager."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("groups.editManager", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def enableOnline(self, group_id:Optional[int]=None) -> BaseOkResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("groups.enableOnline", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def get(self, user_id:Optional[int]=None, extended:Optional[bool]=None, filter:Optional[list]=None, fields:Optional[list]=None, offset:Optional[int]=None, count:Optional[int]=None) -> GroupsGetResponse| GroupsGetObjectExtendedResponse:
		"""Returns a list of the communities to which a user belongs."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("groups.get", **args)
		models = [GroupsGetResponse, GroupsGetObjectExtendedResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getAddresses(self, group_id:Optional[int]=None, address_ids:Optional[list]=None, latitude:Optional[int]=None, longitude:Optional[int]=None, offset:Optional[int]=None, count:Optional[int]=None, fields:Optional[list]=None) -> GroupsGetAddressesResponse:
		"""Returns a list of community addresses."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("groups.getAddresses", **args)
		models = [GroupsGetAddressesResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getBanned(self, group_id:Optional[int]=None, offset:Optional[int]=None, count:Optional[int]=None, fields:Optional[list]=None, owner_id:Optional[int]=None) -> GroupsGetBannedResponse:
		"""Returns a list of users on a community blacklist."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("groups.getBanned", **args)
		models = [GroupsGetBannedResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getById(self, group_ids:Optional[list]=None, group_id:Optional[str|int]=None, fields:Optional[list]=None) -> GroupsGetByIdObjectLegacyResponse:
		"""Returns information about communities by their IDs."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("groups.getById", **args)
		models = [GroupsGetByIdObjectLegacyResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getCallbackConfirmationCode(self, group_id:Optional[int]=None) -> GroupsGetCallbackConfirmationCodeResponse:
		"""Returns Callback API confirmation code for the community."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("groups.getCallbackConfirmationCode", **args)
		models = [GroupsGetCallbackConfirmationCodeResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getCallbackServers(self, group_id:Optional[int]=None, server_ids:Optional[list]=None) -> GroupsGetCallbackServersResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("groups.getCallbackServers", **args)
		models = [GroupsGetCallbackServersResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getCallbackSettings(self, group_id:Optional[int]=None, server_id:Optional[int]=None) -> GroupsGetCallbackSettingsResponse:
		"""Returns [vk.com/dev/callback_api|Callback API] notifications settings."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("groups.getCallbackSettings", **args)
		models = [GroupsGetCallbackSettingsResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getCatalog(self, category_id:Optional[int]=None, subcategory_id:Optional[int]=None) -> GroupsGetCatalogResponse:
		"""Returns communities list for a catalog category."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("groups.getCatalog", **args)
		models = [GroupsGetCatalogResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getCatalogInfo(self, extended:Optional[bool]=None, subcategories:Optional[bool]=None) -> GroupsGetCatalogInfoResponse| GroupsGetCatalogInfoExtendedResponse:
		"""Returns categories list for communities catalog"""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("groups.getCatalogInfo", **args)
		models = [GroupsGetCatalogInfoResponse, GroupsGetCatalogInfoExtendedResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getInvitedUsers(self, group_id:Optional[int]=None, offset:Optional[int]=None, count:Optional[int]=None, fields:Optional[list]=None, name_case:Optional[str]=None) -> GroupsGetInvitedUsersResponse:
		"""Returns invited users list of a community"""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("groups.getInvitedUsers", **args)
		models = [GroupsGetInvitedUsersResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getInvites(self, offset:Optional[int]=None, count:Optional[int]=None, extended:Optional[bool]=None) -> GroupsGetInvitesResponse| GroupsGetInvitesExtendedResponse:
		"""Returns a list of invitations to join communities and events."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("groups.getInvites", **args)
		models = [GroupsGetInvitesResponse, GroupsGetInvitesExtendedResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getLongPollServer(self, group_id:Optional[int]=None) -> GroupsGetLongPollServerResponse:
		"""Returns the data needed to query a Long Poll server for events"""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("groups.getLongPollServer", **args)
		models = [GroupsGetLongPollServerResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getLongPollSettings(self, group_id:Optional[int]=None) -> GroupsGetLongPollSettingsResponse:
		"""Returns Long Poll notification settings"""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("groups.getLongPollSettings", **args)
		models = [GroupsGetLongPollSettingsResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getMembers(self, group_id:Optional[str]=None, sort:Optional[str]=None, offset:Optional[int]=None, count:Optional[int]=None, fields:Optional[list]=None, filter:Optional[str]=None) -> GroupsGetMembersResponse| GroupsGetMembersFieldsResponse| GroupsGetMembersFilterResponse:
		"""Returns a list of community members."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("groups.getMembers", **args)
		models = [GroupsGetMembersResponse, GroupsGetMembersFieldsResponse, GroupsGetMembersFilterResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getRequests(self, group_id:Optional[int]=None, offset:Optional[int]=None, count:Optional[int]=None, fields:Optional[list]=None) -> GroupsGetRequestsResponse| GroupsGetRequestsFieldsResponse:
		"""Returns a list of requests to the community."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("groups.getRequests", **args)
		models = [GroupsGetRequestsResponse, GroupsGetRequestsFieldsResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getSettings(self, group_id:Optional[int]=None) -> GroupsGetSettingsResponse:
		"""Returns community settings."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("groups.getSettings", **args)
		models = [GroupsGetSettingsResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getTagList(self, group_id:Optional[int]=None) -> GroupsGetTagListResponse:
		"""List of group's tags"""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("groups.getTagList", **args)
		models = [GroupsGetTagListResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getTokenPermissions(self) -> GroupsGetTokenPermissionsResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("groups.getTokenPermissions", **args)
		models = [GroupsGetTokenPermissionsResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def invite(self, group_id:Optional[int]=None, user_id:Optional[int]=None) -> BaseOkResponse:
		"""Allows to invite friends to the community."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("groups.invite", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def isMember(self, group_id:Optional[str]=None, user_id:Optional[int]=None, user_ids:Optional[list]=None, extended:Optional[bool]=None) -> GroupsIsMemberResponse| GroupsIsMemberUserIdsResponse| GroupsIsMemberExtendedResponse| GroupsIsMemberUserIdsExtendedResponse:
		"""Returns information specifying whether a user is a member of a community."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("groups.isMember", **args)
		models = [GroupsIsMemberResponse, GroupsIsMemberUserIdsResponse, GroupsIsMemberExtendedResponse, GroupsIsMemberUserIdsExtendedResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def join(self, group_id:Optional[int]=None, not_sure:Optional[str]=None) -> BaseOkResponse:
		"""With this method you can join the group or public page, and also confirm your participation in an event."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("groups.join", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def leave(self, group_id:Optional[int]=None) -> BaseOkResponse:
		"""With this method you can leave a group, public page, or event."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("groups.leave", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def removeUser(self, group_id:Optional[int]=None, user_id:Optional[int]=None) -> BaseOkResponse:
		"""Removes a user from the community."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("groups.removeUser", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def reorderLink(self, group_id:Optional[int]=None, link_id:Optional[int]=None, after:Optional[int]=None) -> BaseOkResponse:
		"""Allows to reorder links in the community."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("groups.reorderLink", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def search(self, q:Optional[str]=None, type:Optional[str]=None, country_id:Optional[int]=None, city_id:Optional[int]=None, future:Optional[bool]=None, market:Optional[bool]=None, sort:Optional[int]=None, offset:Optional[int]=None, count:Optional[int]=None) -> GroupsSearchResponse:
		"""Returns a list of communities matching the search criteria."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("groups.search", **args)
		models = [GroupsSearchResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def setCallbackSettings(self, group_id:Optional[int]=None, server_id:Optional[int]=None, api_version:Optional[str]=None, message_new:Optional[bool]=None, message_reply:Optional[bool]=None, message_allow:Optional[bool]=None, message_edit:Optional[bool]=None, message_deny:Optional[bool]=None, message_typing_state:Optional[bool]=None, photo_new:Optional[bool]=None, audio_new:Optional[bool]=None, video_new:Optional[bool]=None, wall_reply_new:Optional[bool]=None, wall_reply_edit:Optional[bool]=None, wall_reply_delete:Optional[bool]=None, wall_reply_restore:Optional[bool]=None, wall_post_new:Optional[bool]=None, wall_repost:Optional[bool]=None, board_post_new:Optional[bool]=None, board_post_edit:Optional[bool]=None, board_post_restore:Optional[bool]=None, board_post_delete:Optional[bool]=None, photo_comment_new:Optional[bool]=None, photo_comment_edit:Optional[bool]=None, photo_comment_delete:Optional[bool]=None, photo_comment_restore:Optional[bool]=None, video_comment_new:Optional[bool]=None, video_comment_edit:Optional[bool]=None, video_comment_delete:Optional[bool]=None, video_comment_restore:Optional[bool]=None, market_comment_new:Optional[bool]=None, market_comment_edit:Optional[bool]=None, market_comment_delete:Optional[bool]=None, market_comment_restore:Optional[bool]=None, market_order_new:Optional[bool]=None, market_order_edit:Optional[bool]=None, poll_vote_new:Optional[bool]=None, group_join:Optional[bool]=None, group_leave:Optional[bool]=None, group_change_settings:Optional[bool]=None, group_change_photo:Optional[bool]=None, group_officers_edit:Optional[bool]=None, user_block:Optional[bool]=None, user_unblock:Optional[bool]=None, lead_forms_new:Optional[bool]=None, like_add:Optional[bool]=None, like_remove:Optional[bool]=None, message_event:Optional[bool]=None, donut_subscription_create:Optional[bool]=None, donut_subscription_prolonged:Optional[bool]=None, donut_subscription_cancelled:Optional[bool]=None, donut_subscription_price_changed:Optional[bool]=None, donut_subscription_expired:Optional[bool]=None, donut_money_withdraw:Optional[bool]=None, donut_money_withdraw_error:Optional[bool]=None) -> BaseOkResponse:
		"""Allow to set notifications settings for group."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("groups.setCallbackSettings", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def setLongPollSettings(self, group_id:Optional[int]=None, enabled:Optional[bool]=None, api_version:Optional[str]=None, message_new:Optional[bool]=None, message_reply:Optional[bool]=None, message_allow:Optional[bool]=None, message_deny:Optional[bool]=None, message_edit:Optional[bool]=None, message_typing_state:Optional[bool]=None, photo_new:Optional[bool]=None, audio_new:Optional[bool]=None, video_new:Optional[bool]=None, wall_reply_new:Optional[bool]=None, wall_reply_edit:Optional[bool]=None, wall_reply_delete:Optional[bool]=None, wall_reply_restore:Optional[bool]=None, wall_post_new:Optional[bool]=None, wall_repost:Optional[bool]=None, board_post_new:Optional[bool]=None, board_post_edit:Optional[bool]=None, board_post_restore:Optional[bool]=None, board_post_delete:Optional[bool]=None, photo_comment_new:Optional[bool]=None, photo_comment_edit:Optional[bool]=None, photo_comment_delete:Optional[bool]=None, photo_comment_restore:Optional[bool]=None, video_comment_new:Optional[bool]=None, video_comment_edit:Optional[bool]=None, video_comment_delete:Optional[bool]=None, video_comment_restore:Optional[bool]=None, market_comment_new:Optional[bool]=None, market_comment_edit:Optional[bool]=None, market_comment_delete:Optional[bool]=None, market_comment_restore:Optional[bool]=None, poll_vote_new:Optional[bool]=None, group_join:Optional[bool]=None, group_leave:Optional[bool]=None, group_change_settings:Optional[bool]=None, group_change_photo:Optional[bool]=None, group_officers_edit:Optional[bool]=None, user_block:Optional[bool]=None, user_unblock:Optional[bool]=None, like_add:Optional[bool]=None, like_remove:Optional[bool]=None, message_event:Optional[bool]=None, donut_subscription_create:Optional[bool]=None, donut_subscription_prolonged:Optional[bool]=None, donut_subscription_cancelled:Optional[bool]=None, donut_subscription_price_changed:Optional[bool]=None, donut_subscription_expired:Optional[bool]=None, donut_money_withdraw:Optional[bool]=None, donut_money_withdraw_error:Optional[bool]=None) -> BaseOkResponse:
		"""Sets Long Poll notification settings"""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("groups.setLongPollSettings", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def setSettings(self, group_id:Optional[int]=None, messages:Optional[bool]=None, bots_capabilities:Optional[bool]=None, bots_start_button:Optional[bool]=None, bots_add_to_chat:Optional[bool]=None) -> BaseOkResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("groups.setSettings", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def setUserNote(self, group_id:Optional[int]=None, user_id:Optional[int]=None, note:Optional[str]=None) -> BaseBoolResponse:
		"""In order to save note about group participant"""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("groups.setUserNote", **args)
		models = [BaseBoolResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def tagAdd(self, group_id:Optional[int]=None, tag_name:Optional[str]=None, tag_color:Optional[str]=None) -> BaseBoolResponse:
		"""Add new group's tag"""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("groups.tagAdd", **args)
		models = [BaseBoolResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def tagBind(self, group_id:Optional[int]=None, tag_id:Optional[int]=None, user_id:Optional[int]=None, act:Optional[str]=None) -> BaseBoolResponse:
		"""Bind or unbind group's tag to user"""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("groups.tagBind", **args)
		models = [BaseBoolResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def tagDelete(self, group_id:Optional[int]=None, tag_id:Optional[int]=None) -> BaseBoolResponse:
		"""Delete group's tag"""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("groups.tagDelete", **args)
		models = [BaseBoolResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def tagUpdate(self, group_id:Optional[int]=None, tag_id:Optional[int]=None, tag_name:Optional[str]=None) -> BaseBoolResponse:
		"""Update group's tag"""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("groups.tagUpdate", **args)
		models = [BaseBoolResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def toggleMarket(self, group_id:Optional[int]=None, state:Optional[str]=None, ref:Optional[str]=None) -> BaseOkResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("groups.toggleMarket", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def unban(self, group_id:Optional[int]=None, owner_id:Optional[int]=None) -> BaseOkResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("groups.unban", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)



class Leadforms(BaseMethod):
	def __init__(self, vk):
		super().__init__(vk)

	async def create(self, group_id:Optional[int]=None, name:Optional[str]=None, title:Optional[str]=None, description:Optional[str]=None, questions:Optional[str]=None, policy_link_url:Optional[str]=None, photo:Optional[str]=None, confirmation:Optional[str]=None, site_link_url:Optional[str]=None, active:Optional[bool]=None, once_per_user:Optional[bool]=None, pixel_code:Optional[str]=None, notify_admins:Optional[list]=None, notify_emails:Optional[list]=None) -> LeadFormsCreateResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("leadforms.create", **args)
		models = [LeadFormsCreateResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def delete(self, group_id:Optional[int]=None, form_id:Optional[int]=None) -> LeadFormsDeleteResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("leadforms.delete", **args)
		models = [LeadFormsDeleteResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def get(self, group_id:Optional[int]=None, form_id:Optional[int]=None) -> LeadFormsGetResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("leadforms.get", **args)
		models = [LeadFormsGetResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getLeads(self, group_id:Optional[int]=None, form_id:Optional[int]=None, limit:Optional[int]=None, next_page_token:Optional[str]=None) -> LeadFormsGetLeadsResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("leadforms.getLeads", **args)
		models = [LeadFormsGetLeadsResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getUploadURL(self) -> LeadFormsUploadUrlResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("leadforms.getUploadURL", **args)
		models = [LeadFormsUploadUrlResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def _list(self, group_id:Optional[int]=None) -> LeadFormsListResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("leadforms._list", **args)
		models = [LeadFormsListResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def update(self, group_id:Optional[int]=None, form_id:Optional[int]=None, name:Optional[str]=None, title:Optional[str]=None, description:Optional[str]=None, questions:Optional[str]=None, policy_link_url:Optional[str]=None, photo:Optional[str]=None, confirmation:Optional[str]=None, site_link_url:Optional[str]=None, active:Optional[bool]=None, once_per_user:Optional[bool]=None, pixel_code:Optional[str]=None, notify_admins:Optional[list]=None, notify_emails:Optional[list]=None) -> LeadFormsCreateResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("leadforms.update", **args)
		models = [LeadFormsCreateResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)



class Likes(BaseMethod):
	def __init__(self, vk):
		super().__init__(vk)

	async def add(self, type:Optional[str]=None, owner_id:Optional[int]=None, item_id:Optional[int]=None, access_key:Optional[str]=None) -> LikesAddResponse:
		"""Adds the specified object to the 'Likes' list of the current user."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("likes.add", **args)
		models = [LikesAddResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def delete(self, type:Optional[str]=None, owner_id:Optional[int]=None, item_id:Optional[int]=None, access_key:Optional[str]=None) -> LikesDeleteResponse:
		"""Deletes the specified object from the 'Likes' list of the current user."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("likes.delete", **args)
		models = [LikesDeleteResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getList(self, type:Optional[str]=None, owner_id:Optional[int]=None, item_id:Optional[int]=None, page_url:Optional[str]=None, filter:Optional[str]=None, friends_only:Optional[int]=None, extended:Optional[bool]=None, offset:Optional[int]=None, count:Optional[int]=None, skip_own:Optional[bool]=None) -> LikesGetListResponse| LikesGetListExtendedResponse:
		"""Returns a list of IDs of users who added the specified object to their 'Likes' list."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("likes.getList", **args)
		models = [LikesGetListResponse, LikesGetListExtendedResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def isLiked(self, user_id:Optional[int]=None, type:Optional[str]=None, owner_id:Optional[int]=None, item_id:Optional[int]=None) -> LikesIsLikedResponse:
		"""Checks for the object in the 'Likes' list of the specified user."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("likes.isLiked", **args)
		models = [LikesIsLikedResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)



class Market(BaseMethod):
	def __init__(self, vk):
		super().__init__(vk)

	async def add(self, owner_id:Optional[int]=None, name:Optional[str]=None, description:Optional[str]=None, category_id:Optional[int]=None, price:Optional[int]=None, old_price:Optional[int]=None, deleted:Optional[bool]=None, main_photo_id:Optional[int]=None, photo_ids:Optional[list]=None, url:Optional[str]=None, dimension_width:Optional[int]=None, dimension_height:Optional[int]=None, dimension_length:Optional[int]=None, weight:Optional[int]=None, sku:Optional[str]=None) -> MarketAddResponse:
		"""Ads a new item to the market."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("market.add", **args)
		models = [MarketAddResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def addAlbum(self, owner_id:Optional[int]=None, title:Optional[str]=None, photo_id:Optional[int]=None, main_album:Optional[bool]=None, is_hidden:Optional[bool]=None) -> MarketAddAlbumResponse:
		"""Creates new collection of items"""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("market.addAlbum", **args)
		models = [MarketAddAlbumResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def addToAlbum(self, owner_id:Optional[int]=None, item_ids:Optional[list]=None, album_ids:Optional[list]=None) -> BaseOkResponse:
		"""Adds an item to one or multiple collections."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("market.addToAlbum", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def createComment(self, owner_id:Optional[int]=None, item_id:Optional[int]=None, message:Optional[str]=None, attachments:Optional[str]=None, from_group:Optional[bool]=None, reply_to_comment:Optional[int]=None, sticker_id:Optional[int]=None, guid:Optional[str]=None) -> MarketCreateCommentResponse:
		"""Creates a new comment for an item."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("market.createComment", **args)
		models = [MarketCreateCommentResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def delete(self, owner_id:Optional[int]=None, item_id:Optional[int]=None) -> BaseOkResponse:
		"""Deletes an item."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("market.delete", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def deleteAlbum(self, owner_id:Optional[int]=None, album_id:Optional[int]=None) -> BaseOkResponse:
		"""Deletes a collection of items."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("market.deleteAlbum", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def deleteComment(self, owner_id:Optional[int]=None, comment_id:Optional[int]=None) -> MarketDeleteCommentResponse:
		"""Deletes an item's comment"""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("market.deleteComment", **args)
		models = [MarketDeleteCommentResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def edit(self, owner_id:Optional[int]=None, item_id:Optional[int]=None, name:Optional[str]=None, description:Optional[str]=None, category_id:Optional[int]=None, price:Optional[int]=None, old_price:Optional[int]=None, deleted:Optional[bool]=None, main_photo_id:Optional[int]=None, photo_ids:Optional[list]=None, url:Optional[str]=None, dimension_width:Optional[int]=None, dimension_height:Optional[int]=None, dimension_length:Optional[int]=None, weight:Optional[int]=None, sku:Optional[str]=None) -> BaseOkResponse:
		"""Edits an item."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("market.edit", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def editAlbum(self, owner_id:Optional[int]=None, album_id:Optional[int]=None, title:Optional[str]=None, photo_id:Optional[int]=None, main_album:Optional[bool]=None, is_hidden:Optional[bool]=None) -> BaseOkResponse:
		"""Edits a collection of items"""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("market.editAlbum", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def editComment(self, owner_id:Optional[int]=None, comment_id:Optional[int]=None, message:Optional[str]=None, attachments:Optional[str]=None) -> BaseOkResponse:
		"""Chages item comment's text"""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("market.editComment", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def editOrder(self, user_id:Optional[int]=None, order_id:Optional[int]=None, merchant_comment:Optional[str]=None, status:Optional[int]=None, track_number:Optional[str]=None, payment_status:Optional[str]=None, delivery_price:Optional[int]=None, width:Optional[int]=None, length:Optional[int]=None, height:Optional[int]=None, weight:Optional[int]=None) -> BaseOkResponse:
		"""Edit order"""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("market.editOrder", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def get(self, owner_id:Optional[int]=None, album_id:Optional[int]=None, count:Optional[int]=None, offset:Optional[int]=None, extended:Optional[bool]=None, date_from:Optional[str]=None, date_to:Optional[str]=None, need_variants:Optional[bool]=None, with_disabled:Optional[bool]=None) -> MarketGetResponse| MarketGetExtendedResponse:
		"""Returns items list for a community."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("market.get", **args)
		models = [MarketGetResponse, MarketGetExtendedResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getAlbumById(self, owner_id:Optional[int]=None, album_ids:Optional[list]=None) -> MarketGetAlbumByIdResponse:
		"""Returns items album's data"""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("market.getAlbumById", **args)
		models = [MarketGetAlbumByIdResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getAlbums(self, owner_id:Optional[int]=None, offset:Optional[int]=None, count:Optional[int]=None) -> MarketGetAlbumsResponse:
		"""Returns community's market collections list."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("market.getAlbums", **args)
		models = [MarketGetAlbumsResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getById(self, item_ids:Optional[list]=None, extended:Optional[bool]=None) -> MarketGetByIdResponse| MarketGetByIdExtendedResponse:
		"""Returns information about market items by their ids."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("market.getById", **args)
		models = [MarketGetByIdResponse, MarketGetByIdExtendedResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getCategories(self, count:Optional[int]=None, offset:Optional[int]=None) -> MarketGetCategoriesResponse:
		"""Returns a list of market categories."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("market.getCategories", **args)
		models = [MarketGetCategoriesResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getComments(self, owner_id:Optional[int]=None, item_id:Optional[int]=None, need_likes:Optional[bool]=None, start_comment_id:Optional[int]=None, offset:Optional[int]=None, count:Optional[int]=None, sort:Optional[str]=None, extended:Optional[bool]=None, fields:Optional[list]=None) -> MarketGetCommentsResponse:
		"""Returns comments list for an item."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("market.getComments", **args)
		models = [MarketGetCommentsResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getGroupOrders(self, group_id:Optional[int]=None, offset:Optional[int]=None, count:Optional[int]=None) -> MarketGetGroupOrdersResponse:
		"""Get market orders"""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("market.getGroupOrders", **args)
		models = [MarketGetGroupOrdersResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getOrderById(self, user_id:Optional[int]=None, order_id:Optional[int]=None, extended:Optional[bool]=None) -> MarketGetOrderByIdResponse:
		"""Get order"""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("market.getOrderById", **args)
		models = [MarketGetOrderByIdResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getOrderItems(self, user_id:Optional[int]=None, order_id:Optional[int]=None, offset:Optional[int]=None, count:Optional[int]=None) -> MarketGetOrderItemsResponse:
		"""Get market items in the order"""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("market.getOrderItems", **args)
		models = [MarketGetOrderItemsResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getOrders(self, offset:Optional[int]=None, count:Optional[int]=None, extended:Optional[bool]=None, date_from:Optional[str]=None, date_to:Optional[str]=None) -> MarketGetOrdersResponse| MarketGetOrdersExtendedResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("market.getOrders", **args)
		models = [MarketGetOrdersResponse, MarketGetOrdersExtendedResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def removeFromAlbum(self, owner_id:Optional[int]=None, item_id:Optional[int]=None, album_ids:Optional[list]=None) -> BaseOkResponse:
		"""Removes an item from one or multiple collections."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("market.removeFromAlbum", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def reorderAlbums(self, owner_id:Optional[int]=None, album_id:Optional[int]=None, before:Optional[int]=None, after:Optional[int]=None) -> BaseOkResponse:
		"""Reorders the collections list."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("market.reorderAlbums", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def reorderItems(self, owner_id:Optional[int]=None, album_id:Optional[int]=None, item_id:Optional[int]=None, before:Optional[int]=None, after:Optional[int]=None) -> BaseOkResponse:
		"""Changes item place in a collection."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("market.reorderItems", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def report(self, owner_id:Optional[int]=None, item_id:Optional[int]=None, reason:Optional[int]=None) -> BaseOkResponse:
		"""Sends a complaint to the item."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("market.report", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def reportComment(self, owner_id:Optional[int]=None, comment_id:Optional[int]=None, reason:Optional[int]=None) -> BaseOkResponse:
		"""Sends a complaint to the item's comment."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("market.reportComment", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def restore(self, owner_id:Optional[int]=None, item_id:Optional[int]=None) -> BaseOkResponse:
		"""Restores recently deleted item"""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("market.restore", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def restoreComment(self, owner_id:Optional[int]=None, comment_id:Optional[int]=None) -> MarketRestoreCommentResponse:
		"""Restores a recently deleted comment"""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("market.restoreComment", **args)
		models = [MarketRestoreCommentResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def search(self, owner_id:Optional[int]=None, album_id:Optional[int]=None, q:Optional[str]=None, price_from:Optional[int]=None, price_to:Optional[int]=None, sort:Optional[int]=None, rev:Optional[int]=None, offset:Optional[int]=None, count:Optional[int]=None, extended:Optional[bool]=None, status:Optional[list]=None, need_variants:Optional[bool]=None) -> MarketSearchResponse| MarketSearchExtendedResponse:
		"""Searches market items in a community's catalog"""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("market.search", **args)
		models = [MarketSearchResponse, MarketSearchExtendedResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def searchItems(self, q:Optional[str]=None, offset:Optional[int]=None, count:Optional[int]=None, category_id:Optional[int]=None, price_from:Optional[int]=None, price_to:Optional[int]=None, sort_by:Optional[int]=None, sort_direction:Optional[int]=None, country:Optional[int]=None, city:Optional[int]=None) -> MarketSearchResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("market.searchItems", **args)
		models = [MarketSearchResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)



class Messages(BaseMethod):
	def __init__(self, vk):
		super().__init__(vk)

	async def addChatUser(self, chat_id:Optional[int]=None, user_id:Optional[int]=None, visible_messages_count:Optional[int]=None) -> BaseOkResponse:
		"""Adds a new user to a chat."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("messages.addChatUser", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def allowMessagesFromGroup(self, group_id:Optional[int]=None, key:Optional[str]=None) -> BaseOkResponse:
		"""Allows sending messages from community to the current user."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("messages.allowMessagesFromGroup", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def createChat(self, user_ids:Optional[list]=None, title:Optional[str]=None, group_id:Optional[int]=None) -> MessagesCreateChatResponse:
		"""Creates a chat with several participants."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("messages.createChat", **args)
		models = [MessagesCreateChatResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def delete(self, message_ids:Optional[list]=None, spam:Optional[bool]=None, group_id:Optional[int]=None, delete_for_all:Optional[bool]=None, peer_id:Optional[int]=None, cmids:Optional[list]=None) -> MessagesDeleteResponse:
		"""Deletes one or more messages."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("messages.delete", **args)
		models = [MessagesDeleteResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def deleteChatPhoto(self, chat_id:Optional[int]=None, group_id:Optional[int]=None) -> MessagesDeleteChatPhotoResponse:
		"""Deletes a chat's cover picture."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("messages.deleteChatPhoto", **args)
		models = [MessagesDeleteChatPhotoResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def deleteConversation(self, user_id:Optional[int]=None, peer_id:Optional[int]=None, group_id:Optional[int]=None) -> MessagesDeleteConversationResponse:
		"""Deletes all private messages in a conversation."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("messages.deleteConversation", **args)
		models = [MessagesDeleteConversationResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def denyMessagesFromGroup(self, group_id:Optional[int]=None) -> BaseOkResponse:
		"""Denies sending message from community to the current user."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("messages.denyMessagesFromGroup", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def edit(self, peer_id:Optional[int]=None, message:Optional[str]=None, lat:Optional[int]=None, long:Optional[int]=None, attachment:Optional[str]=None, keep_forward_messages:Optional[bool]=None, keep_snippets:Optional[bool]=None, group_id:Optional[int]=None, dont_parse_links:Optional[bool]=None, disable_mentions:Optional[bool]=None, message_id:Optional[int]=None, conversation_message_id:Optional[int]=None, template:Optional[str]=None, keyboard:Optional[str]=None) -> MessagesEditResponse:
		"""Edits the message."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("messages.edit", **args)
		models = [MessagesEditResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def editChat(self, chat_id:Optional[int]=None, title:Optional[str]=None) -> BaseOkResponse:
		"""Edits the title of a chat."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("messages.editChat", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getByConversationMessageId(self, peer_id:Optional[int]=None, conversation_message_ids:Optional[list]=None, extended:Optional[bool]=None, fields:Optional[list]=None, group_id:Optional[int]=None) -> MessagesGetByConversationMessageIdResponse| MessagesGetByConversationMessageIdExtendedResponse:
		"""Returns messages by their IDs within the conversation."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("messages.getByConversationMessageId", **args)
		models = [MessagesGetByConversationMessageIdResponse, MessagesGetByConversationMessageIdExtendedResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getById(self, message_ids:Optional[list]=None, preview_length:Optional[int]=None, extended:Optional[bool]=None, fields:Optional[list]=None, group_id:Optional[int]=None) -> MessagesGetByIdResponse| MessagesGetByIdExtendedResponse:
		"""Returns messages by their IDs."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("messages.getById", **args)
		models = [MessagesGetByIdResponse, MessagesGetByIdExtendedResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getChatPreview(self, peer_id:Optional[int]=None, link:Optional[str]=None, fields:Optional[list]=None) -> MessagesGetChatPreviewResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("messages.getChatPreview", **args)
		models = [MessagesGetChatPreviewResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getConversationMembers(self, peer_id:Optional[int]=None, fields:Optional[list]=None, group_id:Optional[int]=None) -> MessagesGetConversationMembersResponse:
		"""Returns a list of IDs of users participating in a chat."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("messages.getConversationMembers", **args)
		models = [MessagesGetConversationMembersResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getConversations(self, offset:Optional[int]=None, count:Optional[int]=None, filter:Optional[str]=None, extended:Optional[bool]=None, start_message_id:Optional[int]=None, fields:Optional[list]=None, group_id:Optional[int]=None) -> MessagesGetConversationsResponse:
		"""Returns a list of the current user's conversations."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("messages.getConversations", **args)
		models = [MessagesGetConversationsResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getConversationsById(self, peer_ids:Optional[list]=None, extended:Optional[bool]=None, fields:Optional[list]=None, group_id:Optional[int]=None) -> MessagesGetConversationsByIdResponse| MessagesGetConversationsByIdExtendedResponse:
		"""Returns conversations by their IDs"""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("messages.getConversationsById", **args)
		models = [MessagesGetConversationsByIdResponse, MessagesGetConversationsByIdExtendedResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getHistory(self, offset:Optional[int]=None, count:Optional[int]=None, user_id:Optional[int]=None, peer_id:Optional[int]=None, start_message_id:Optional[int]=None, rev:Optional[int]=None, extended:Optional[bool]=None, fields:Optional[list]=None, group_id:Optional[int]=None) -> MessagesGetHistoryResponse| MessagesGetHistoryExtendedResponse:
		"""Returns message history for the specified user or group chat."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("messages.getHistory", **args)
		models = [MessagesGetHistoryResponse, MessagesGetHistoryExtendedResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getHistoryAttachments(self, peer_id:Optional[int]=None, media_type:Optional[str]=None, start_from:Optional[str]=None, count:Optional[int]=None, photo_sizes:Optional[bool]=None, fields:Optional[list]=None, group_id:Optional[int]=None, preserve_order:Optional[bool]=None, max_forwards_level:Optional[int]=None) -> MessagesGetHistoryAttachmentsResponse:
		"""Returns media files from the dialog or group chat."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("messages.getHistoryAttachments", **args)
		models = [MessagesGetHistoryAttachmentsResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getImportantMessages(self, count:Optional[int]=None, offset:Optional[int]=None, start_message_id:Optional[int]=None, preview_length:Optional[int]=None, fields:Optional[list]=None, extended:Optional[bool]=None, group_id:Optional[int]=None) -> MessagesGetImportantMessagesResponse| MessagesGetImportantMessagesExtendedResponse:
		"""Returns a list of user's important messages."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("messages.getImportantMessages", **args)
		models = [MessagesGetImportantMessagesResponse, MessagesGetImportantMessagesExtendedResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getIntentUsers(self, intent:Optional[str]=None, subscribe_id:Optional[int]=None, offset:Optional[int]=None, count:Optional[int]=None, extended:Optional[bool]=None, name_case:Optional[list]=None, fields:Optional[list]=None) -> MessagesGetIntentUsersResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("messages.getIntentUsers", **args)
		models = [MessagesGetIntentUsersResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getInviteLink(self, peer_id:Optional[int]=None, reset:Optional[bool]=None, group_id:Optional[int]=None) -> MessagesGetInviteLinkResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("messages.getInviteLink", **args)
		models = [MessagesGetInviteLinkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getLastActivity(self, user_id:Optional[int]=None) -> MessagesGetLastActivityResponse:
		"""Returns a user's current status and date of last activity."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("messages.getLastActivity", **args)
		models = [MessagesGetLastActivityResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getLongPollHistory(self, ts:Optional[int]=None, pts:Optional[int]=None, preview_length:Optional[int]=None, onlines:Optional[bool]=None, fields:Optional[list]=None, events_limit:Optional[int]=None, msgs_limit:Optional[int]=None, max_msg_id:Optional[int]=None, group_id:Optional[int]=None, lp_version:Optional[int]=None, last_n:Optional[int]=None, credentials:Optional[bool]=None, extended:Optional[bool]=None) -> MessagesGetLongPollHistoryResponse:
		"""Returns updates in user's private messages."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("messages.getLongPollHistory", **args)
		models = [MessagesGetLongPollHistoryResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getLongPollServer(self, need_pts:Optional[bool]=None, group_id:Optional[int]=None, lp_version:Optional[int]=None) -> MessagesGetLongPollServerResponse:
		"""Returns data required for connection to a Long Poll server."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("messages.getLongPollServer", **args)
		models = [MessagesGetLongPollServerResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def isMessagesFromGroupAllowed(self, group_id:Optional[int]=None, user_id:Optional[int]=None) -> MessagesIsMessagesFromGroupAllowedResponse:
		"""Returns information whether sending messages from the community to current user is allowed."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("messages.isMessagesFromGroupAllowed", **args)
		models = [MessagesIsMessagesFromGroupAllowedResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def joinChatByInviteLink(self, link:Optional[str]=None) -> MessagesJoinChatByInviteLinkResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("messages.joinChatByInviteLink", **args)
		models = [MessagesJoinChatByInviteLinkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def markAsAnsweredConversation(self, peer_id:Optional[int]=None, answered:Optional[bool]=None, group_id:Optional[int]=None) -> BaseOkResponse:
		"""Marks and unmarks conversations as unanswered."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("messages.markAsAnsweredConversation", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def markAsImportant(self, message_ids:Optional[list]=None, important:Optional[int]=None) -> MessagesMarkAsImportantResponse:
		"""Marks and unmarks messages as important (starred)."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("messages.markAsImportant", **args)
		models = [MessagesMarkAsImportantResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def markAsImportantConversation(self, peer_id:Optional[int]=None, important:Optional[bool]=None, group_id:Optional[int]=None) -> BaseOkResponse:
		"""Marks and unmarks conversations as important."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("messages.markAsImportantConversation", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def markAsRead(self, message_ids:Optional[list]=None, peer_id:Optional[int]=None, start_message_id:Optional[int]=None, group_id:Optional[int]=None, mark_conversation_as_read:Optional[bool]=None) -> BaseOkResponse:
		"""Marks messages as read."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("messages.markAsRead", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def pin(self, peer_id:Optional[int]=None, message_id:Optional[int]=None, conversation_message_id:Optional[int]=None) -> MessagesPinResponse:
		"""Pin a message."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("messages.pin", **args)
		models = [MessagesPinResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def removeChatUser(self, chat_id:Optional[int]=None, user_id:Optional[int]=None, member_id:Optional[int]=None) -> BaseOkResponse:
		"""Allows the current user to leave a chat or, if the current user started the chat, allows the user to remove another user from the chat."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("messages.removeChatUser", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def restore(self, message_id:Optional[int]=None, group_id:Optional[int]=None) -> BaseOkResponse:
		"""Restores a deleted message."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("messages.restore", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def search(self, q:Optional[str]=None, peer_id:Optional[int]=None, date:Optional[int]=None, preview_length:Optional[int]=None, offset:Optional[int]=None, count:Optional[int]=None, extended:Optional[bool]=None, fields:Optional[list]=None, group_id:Optional[int]=None) -> MessagesSearchResponse| MessagesSearchExtendedResponse:
		"""Returns a list of the current user's private messages that match search criteria."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("messages.search", **args)
		models = [MessagesSearchResponse, MessagesSearchExtendedResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def searchConversations(self, q:Optional[str]=None, count:Optional[int]=None, extended:Optional[bool]=None, fields:Optional[list]=None, group_id:Optional[int]=None) -> MessagesSearchConversationsResponse| MessagesSearchConversationsExtendedResponse:
		"""Returns a list of the current user's conversations that match search criteria."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("messages.searchConversations", **args)
		models = [MessagesSearchConversationsResponse, MessagesSearchConversationsExtendedResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def send(self, user_id:Optional[int]=None, random_id:Optional[int]=None, peer_id:Optional[int]=None, peer_ids:Optional[list]=None, domain:Optional[str]=None, chat_id:Optional[int]=None, user_ids:Optional[list]=None, message:Optional[str]=None, lat:Optional[int]=None, long:Optional[int]=None, attachment:Optional[str]=None, reply_to:Optional[int]=None, forward_messages:Optional[list]=None, forward:Optional[str]=None, sticker_id:Optional[int]=None, group_id:Optional[int]=None, keyboard:Optional[str]=None, template:Optional[str]=None, payload:Optional[str]=None, content_source:Optional[str]=None, dont_parse_links:Optional[bool]=None, disable_mentions:Optional[bool]=None, intent:Optional[str]=None, subscribe_id:Optional[int]=None) -> MessagesSendResponse| MessagesSendUserIdsResponse:
		"""Sends a message."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("messages.send", **args)
		models = [MessagesSendResponse, MessagesSendUserIdsResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def sendMessageEventAnswer(self, event_id:Optional[str]=None, user_id:Optional[int]=None, peer_id:Optional[int]=None, event_data:Optional[str]=None) -> BaseOkResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("messages.sendMessageEventAnswer", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def setActivity(self, user_id:Optional[int]=None, type:Optional[str]=None, peer_id:Optional[int]=None, group_id:Optional[int]=None) -> BaseOkResponse:
		"""Changes the status of a user as typing in a conversation."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("messages.setActivity", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def setChatPhoto(self, file:Optional[str]=None) -> MessagesSetChatPhotoResponse:
		"""Sets a previously-uploaded picture as the cover picture of a chat."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("messages.setChatPhoto", **args)
		models = [MessagesSetChatPhotoResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def unpin(self, peer_id:Optional[int]=None, group_id:Optional[int]=None) -> BaseOkResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("messages.unpin", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)



class Newsfeed(BaseMethod):
	def __init__(self, vk):
		super().__init__(vk)

	async def addBan(self, user_ids:Optional[list]=None, group_ids:Optional[list]=None) -> BaseOkResponse:
		"""Prevents news from specified users and communities from appearing in the current user's newsfeed."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("newsfeed.addBan", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def deleteBan(self, user_ids:Optional[list]=None, group_ids:Optional[list]=None) -> BaseOkResponse:
		"""Allows news from previously banned users and communities to be shown in the current user's newsfeed."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("newsfeed.deleteBan", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def deleteList(self, list_id:Optional[int]=None) -> BaseOkResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("newsfeed.deleteList", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def get(self, filters:Optional[list]=None, return_banned:Optional[bool]=None, start_time:Optional[int]=None, end_time:Optional[int]=None, max_photos:Optional[int]=None, source_ids:Optional[str]=None, start_from:Optional[str]=None, count:Optional[int]=None, fields:Optional[list]=None, section:Optional[str]=None) -> NewsfeedGenericResponse:
		"""Returns data required to show newsfeed for the current user."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("newsfeed.get", **args)
		models = [NewsfeedGenericResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getBanned(self, extended:Optional[bool]=None, fields:Optional[list]=None, name_case:Optional[str]=None) -> NewsfeedGetBannedResponse| NewsfeedGetBannedExtendedResponse:
		"""Returns a list of users and communities banned from the current user's newsfeed."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("newsfeed.getBanned", **args)
		models = [NewsfeedGetBannedResponse, NewsfeedGetBannedExtendedResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getComments(self, count:Optional[int]=None, filters:Optional[list]=None, reposts:Optional[str]=None, start_time:Optional[int]=None, end_time:Optional[int]=None, last_comments_count:Optional[int]=None, start_from:Optional[str]=None, fields:Optional[list]=None) -> NewsfeedGetCommentsResponse:
		"""Returns a list of comments in the current user's newsfeed."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("newsfeed.getComments", **args)
		models = [NewsfeedGetCommentsResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getLists(self, list_ids:Optional[list]=None, extended:Optional[bool]=None) -> NewsfeedGetListsResponse| NewsfeedGetListsExtendedResponse:
		"""Returns a list of newsfeeds followed by the current user."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("newsfeed.getLists", **args)
		models = [NewsfeedGetListsResponse, NewsfeedGetListsExtendedResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getMentions(self, owner_id:Optional[int]=None, start_time:Optional[int]=None, end_time:Optional[int]=None, offset:Optional[int]=None, count:Optional[int]=None) -> NewsfeedGetMentionsResponse:
		"""Returns a list of posts on user walls in which the current user is mentioned."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("newsfeed.getMentions", **args)
		models = [NewsfeedGetMentionsResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getRecommended(self, start_time:Optional[int]=None, end_time:Optional[int]=None, max_photos:Optional[int]=None, start_from:Optional[str]=None, count:Optional[int]=None, fields:Optional[list]=None) -> NewsfeedGenericResponse:
		""", Returns a list of newsfeeds recommended to the current user."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("newsfeed.getRecommended", **args)
		models = [NewsfeedGenericResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getSuggestedSources(self, offset:Optional[int]=None, count:Optional[int]=None, shuffle:Optional[bool]=None, fields:Optional[list]=None) -> NewsfeedGetSuggestedSourcesResponse:
		"""Returns communities and users that current user is suggested to follow."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("newsfeed.getSuggestedSources", **args)
		models = [NewsfeedGetSuggestedSourcesResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def ignoreItem(self, type:Optional[str]=None, owner_id:Optional[int]=None, item_id:Optional[int]=None) -> BaseOkResponse:
		"""Hides an item from the newsfeed."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("newsfeed.ignoreItem", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def saveList(self, list_id:Optional[int]=None, title:Optional[str]=None, source_ids:Optional[list]=None, no_reposts:Optional[bool]=None) -> NewsfeedSaveListResponse:
		"""Creates and edits user newsfeed lists"""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("newsfeed.saveList", **args)
		models = [NewsfeedSaveListResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def search(self, q:Optional[str]=None, extended:Optional[bool]=None, count:Optional[int]=None, latitude:Optional[int]=None, longitude:Optional[int]=None, start_time:Optional[int]=None, end_time:Optional[int]=None, start_from:Optional[str]=None, fields:Optional[list]=None) -> NewsfeedSearchResponse| NewsfeedSearchExtendedResponse:
		"""Returns search results by statuses."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("newsfeed.search", **args)
		models = [NewsfeedSearchResponse, NewsfeedSearchExtendedResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def unignoreItem(self, type:Optional[str]=None, owner_id:Optional[int]=None, item_id:Optional[int]=None, track_code:Optional[str]=None) -> BaseOkResponse:
		"""Returns a hidden item to the newsfeed."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("newsfeed.unignoreItem", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def unsubscribe(self, type:Optional[str]=None, owner_id:Optional[int]=None, item_id:Optional[int]=None) -> BaseOkResponse:
		"""Unsubscribes the current user from specified newsfeeds."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("newsfeed.unsubscribe", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)



class Notes(BaseMethod):
	def __init__(self, vk):
		super().__init__(vk)

	async def add(self, title:Optional[str]=None, text:Optional[str]=None, privacy_view:Optional[list]=None, privacy_comment:Optional[list]=None) -> NotesAddResponse:
		"""Creates a new note for the current user."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("notes.add", **args)
		models = [NotesAddResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def createComment(self, note_id:Optional[int]=None, owner_id:Optional[int]=None, reply_to:Optional[int]=None, message:Optional[str]=None, guid:Optional[str]=None) -> NotesCreateCommentResponse:
		"""Adds a new comment on a note."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("notes.createComment", **args)
		models = [NotesCreateCommentResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def delete(self, note_id:Optional[int]=None) -> BaseOkResponse:
		"""Deletes a note of the current user."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("notes.delete", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def deleteComment(self, comment_id:Optional[int]=None, owner_id:Optional[int]=None) -> BaseOkResponse:
		"""Deletes a comment on a note."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("notes.deleteComment", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def edit(self, note_id:Optional[int]=None, title:Optional[str]=None, text:Optional[str]=None, privacy_view:Optional[list]=None, privacy_comment:Optional[list]=None) -> BaseOkResponse:
		"""Edits a note of the current user."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("notes.edit", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def editComment(self, comment_id:Optional[int]=None, owner_id:Optional[int]=None, message:Optional[str]=None) -> BaseOkResponse:
		"""Edits a comment on a note."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("notes.editComment", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def get(self, note_ids:Optional[list]=None, user_id:Optional[int]=None, offset:Optional[int]=None, count:Optional[int]=None, sort:Optional[int]=None) -> NotesGetResponse:
		"""Returns a list of notes created by a user."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("notes.get", **args)
		models = [NotesGetResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getById(self, note_id:Optional[int]=None, owner_id:Optional[int]=None, need_wiki:Optional[bool]=None) -> NotesGetByIdResponse:
		"""Returns a note by its ID."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("notes.getById", **args)
		models = [NotesGetByIdResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getComments(self, note_id:Optional[int]=None, owner_id:Optional[int]=None, sort:Optional[int]=None, offset:Optional[int]=None, count:Optional[int]=None) -> NotesGetCommentsResponse:
		"""Returns a list of comments on a note."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("notes.getComments", **args)
		models = [NotesGetCommentsResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def restoreComment(self, comment_id:Optional[int]=None, owner_id:Optional[int]=None) -> BaseOkResponse:
		"""Restores a deleted comment on a note."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("notes.restoreComment", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)



class Notifications(BaseMethod):
	def __init__(self, vk):
		super().__init__(vk)

	async def get(self, count:Optional[int]=None, start_from:Optional[str]=None, filters:Optional[list]=None, start_time:Optional[int]=None, end_time:Optional[int]=None) -> NotificationsGetResponse:
		"""Returns a list of notifications about other users' feedback to the current user's wall posts."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("notifications.get", **args)
		models = [NotificationsGetResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def markAsViewed(self) -> NotificationsMarkAsViewedResponse:
		"""Resets the counter of new notifications about other users' feedback to the current user's wall posts."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("notifications.markAsViewed", **args)
		models = [NotificationsMarkAsViewedResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def sendMessage(self, user_ids:Optional[list]=None, message:Optional[str]=None, fragment:Optional[str]=None, group_id:Optional[int]=None, random_id:Optional[int]=None, sending_mode:Optional[str]=None) -> NotificationsSendMessageResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("notifications.sendMessage", **args)
		models = [NotificationsSendMessageResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)



class Orders(BaseMethod):
	def __init__(self, vk):
		super().__init__(vk)

	async def cancelSubscription(self, user_id:Optional[int]=None, subscription_id:Optional[int]=None, pending_cancel:Optional[bool]=None) -> OrdersCancelSubscriptionResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("orders.cancelSubscription", **args)
		models = [OrdersCancelSubscriptionResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def changeState(self, order_id:Optional[int]=None, action:Optional[str]=None, app_order_id:Optional[int]=None, test_mode:Optional[bool]=None) -> OrdersChangeStateResponse:
		"""Changes order status."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("orders.changeState", **args)
		models = [OrdersChangeStateResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def get(self, offset:Optional[int]=None, count:Optional[int]=None, test_mode:Optional[bool]=None) -> OrdersGetResponse:
		"""Returns a list of orders."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("orders.get", **args)
		models = [OrdersGetResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getAmount(self, user_id:Optional[int]=None, votes:Optional[list]=None) -> OrdersGetAmountResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("orders.getAmount", **args)
		models = [OrdersGetAmountResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getById(self, order_id:Optional[int]=None, order_ids:Optional[list]=None, test_mode:Optional[bool]=None) -> OrdersGetByIdResponse:
		"""Returns information about orders by their IDs."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("orders.getById", **args)
		models = [OrdersGetByIdResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getUserSubscriptionById(self, user_id:Optional[int]=None, subscription_id:Optional[int]=None) -> OrdersGetUserSubscriptionByIdResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("orders.getUserSubscriptionById", **args)
		models = [OrdersGetUserSubscriptionByIdResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getUserSubscriptions(self, user_id:Optional[int]=None) -> OrdersGetUserSubscriptionsResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("orders.getUserSubscriptions", **args)
		models = [OrdersGetUserSubscriptionsResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def updateSubscription(self, user_id:Optional[int]=None, subscription_id:Optional[int]=None, price:Optional[int]=None) -> OrdersUpdateSubscriptionResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("orders.updateSubscription", **args)
		models = [OrdersUpdateSubscriptionResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)



class Pages(BaseMethod):
	def __init__(self, vk):
		super().__init__(vk)

	async def clearCache(self, url:Optional[str]=None) -> BaseOkResponse:
		"""Allows to clear the cache of particular 'external' pages which may be attached to VK posts."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("pages.clearCache", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def get(self, owner_id:Optional[int]=None, page_id:Optional[int]=None, _global:Optional[bool]=None, site_preview:Optional[bool]=None, title:Optional[str]=None, need_source:Optional[bool]=None, need_html:Optional[bool]=None) -> PagesGetResponse:
		"""Returns information about a wiki page."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("pages.get", **args)
		models = [PagesGetResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getHistory(self, page_id:Optional[int]=None, group_id:Optional[int]=None, user_id:Optional[int]=None) -> PagesGetHistoryResponse:
		"""Returns a list of all previous versions of a wiki page."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("pages.getHistory", **args)
		models = [PagesGetHistoryResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getTitles(self, group_id:Optional[int]=None) -> PagesGetTitlesResponse:
		"""Returns a list of wiki pages in a group."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("pages.getTitles", **args)
		models = [PagesGetTitlesResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getVersion(self, version_id:Optional[int]=None, group_id:Optional[int]=None, user_id:Optional[int]=None, need_html:Optional[bool]=None) -> PagesGetVersionResponse:
		"""Returns the text of one of the previous versions of a wiki page."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("pages.getVersion", **args)
		models = [PagesGetVersionResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def parseWiki(self, text:Optional[str]=None, group_id:Optional[int]=None) -> PagesParseWikiResponse:
		"""Returns HTML representation of the wiki markup."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("pages.parseWiki", **args)
		models = [PagesParseWikiResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def save(self, text:Optional[str]=None, page_id:Optional[int]=None, group_id:Optional[int]=None, user_id:Optional[int]=None, title:Optional[str]=None) -> PagesSaveResponse:
		"""Saves the text of a wiki page."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("pages.save", **args)
		models = [PagesSaveResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def saveAccess(self, page_id:Optional[int]=None, group_id:Optional[int]=None, user_id:Optional[int]=None, view:Optional[int]=None, edit:Optional[int]=None) -> PagesSaveAccessResponse:
		"""Saves modified read and edit access settings for a wiki page."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("pages.saveAccess", **args)
		models = [PagesSaveAccessResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)



class Photos(BaseMethod):
	def __init__(self, vk):
		super().__init__(vk)

	async def confirmTag(self, owner_id:Optional[int]=None, photo_id:Optional[str]=None, tag_id:Optional[int]=None) -> BaseOkResponse:
		"""Confirms a tag on a photo."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("photos.confirmTag", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def copy(self, owner_id:Optional[int]=None, photo_id:Optional[int]=None, access_key:Optional[str]=None) -> PhotosCopyResponse:
		"""Allows to copy a photo to the 'Saved photos' album"""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("photos.copy", **args)
		models = [PhotosCopyResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def createAlbum(self, title:Optional[str]=None, group_id:Optional[int]=None, description:Optional[str]=None, privacy_view:Optional[list]=None, privacy_comment:Optional[list]=None, upload_by_admins_only:Optional[bool]=None, comments_disabled:Optional[bool]=None) -> PhotosCreateAlbumResponse:
		"""Creates an empty photo album."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("photos.createAlbum", **args)
		models = [PhotosCreateAlbumResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def createComment(self, owner_id:Optional[int]=None, photo_id:Optional[int]=None, message:Optional[str]=None, attachments:Optional[str]=None, from_group:Optional[bool]=None, reply_to_comment:Optional[int]=None, sticker_id:Optional[int]=None, access_key:Optional[str]=None, guid:Optional[str]=None) -> PhotosCreateCommentResponse:
		"""Adds a new comment on the photo."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("photos.createComment", **args)
		models = [PhotosCreateCommentResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def delete(self, owner_id:Optional[int]=None, photo_id:Optional[int]=None) -> BaseOkResponse:
		"""Deletes a photo."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("photos.delete", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def deleteAlbum(self, album_id:Optional[int]=None, group_id:Optional[int]=None) -> BaseOkResponse:
		"""Deletes a photo album belonging to the current user."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("photos.deleteAlbum", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def deleteComment(self, owner_id:Optional[int]=None, comment_id:Optional[int]=None) -> PhotosDeleteCommentResponse:
		"""Deletes a comment on the photo."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("photos.deleteComment", **args)
		models = [PhotosDeleteCommentResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def edit(self, owner_id:Optional[int]=None, photo_id:Optional[int]=None, caption:Optional[str]=None, latitude:Optional[int]=None, longitude:Optional[int]=None, place_str:Optional[str]=None, foursquare_id:Optional[str]=None, delete_place:Optional[bool]=None) -> BaseOkResponse:
		"""Edits the caption of a photo."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("photos.edit", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def editAlbum(self, album_id:Optional[int]=None, title:Optional[str]=None, description:Optional[str]=None, owner_id:Optional[int]=None, privacy_view:Optional[list]=None, privacy_comment:Optional[list]=None, upload_by_admins_only:Optional[bool]=None, comments_disabled:Optional[bool]=None) -> BaseOkResponse:
		"""Edits information about a photo album."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("photos.editAlbum", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def editComment(self, owner_id:Optional[int]=None, comment_id:Optional[int]=None, message:Optional[str]=None, attachments:Optional[str]=None) -> BaseOkResponse:
		"""Edits a comment on a photo."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("photos.editComment", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def get(self, owner_id:Optional[int]=None, album_id:Optional[str]=None, photo_ids:Optional[list]=None, rev:Optional[bool]=None, extended:Optional[bool]=None, feed_type:Optional[str]=None, feed:Optional[int]=None, photo_sizes:Optional[bool]=None, offset:Optional[int]=None, count:Optional[int]=None) -> PhotosGetResponse:
		"""Returns a list of a user's or community's photos."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("photos.get", **args)
		models = [PhotosGetResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getAlbums(self, owner_id:Optional[int]=None, album_ids:Optional[list]=None, offset:Optional[int]=None, count:Optional[int]=None, need_system:Optional[bool]=None, need_covers:Optional[bool]=None, photo_sizes:Optional[bool]=None) -> PhotosGetAlbumsResponse:
		"""Returns a list of a user's or community's photo albums."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("photos.getAlbums", **args)
		models = [PhotosGetAlbumsResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getAlbumsCount(self, user_id:Optional[int]=None, group_id:Optional[int]=None) -> PhotosGetAlbumsCountResponse:
		"""Returns the number of photo albums belonging to a user or community."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("photos.getAlbumsCount", **args)
		models = [PhotosGetAlbumsCountResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getAll(self, owner_id:Optional[int]=None, extended:Optional[bool]=None, offset:Optional[int]=None, count:Optional[int]=None, photo_sizes:Optional[bool]=None, no_service_albums:Optional[bool]=None, need_hidden:Optional[bool]=None, skip_hidden:Optional[bool]=None) -> PhotosGetAllResponse| PhotosGetAllExtendedResponse:
		"""Returns a list of photos belonging to a user or community, in reverse chronological order."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("photos.getAll", **args)
		models = [PhotosGetAllResponse, PhotosGetAllExtendedResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getAllComments(self, owner_id:Optional[int]=None, album_id:Optional[int]=None, need_likes:Optional[bool]=None, offset:Optional[int]=None, count:Optional[int]=None) -> PhotosGetAllCommentsResponse:
		"""Returns a list of comments on a specific photo album or all albums of the user sorted in reverse chronological order."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("photos.getAllComments", **args)
		models = [PhotosGetAllCommentsResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getById(self, photos:Optional[list]=None, extended:Optional[bool]=None, photo_sizes:Optional[bool]=None) -> PhotosGetByIdResponse:
		"""Returns information about photos by their IDs."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("photos.getById", **args)
		models = [PhotosGetByIdResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getChatUploadServer(self, chat_id:Optional[int]=None, crop_x:Optional[int]=None, crop_y:Optional[int]=None, crop_width:Optional[int]=None) -> BaseGetUploadServerResponse:
		"""Returns an upload link for chat cover pictures."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("photos.getChatUploadServer", **args)
		models = [BaseGetUploadServerResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getComments(self, owner_id:Optional[int]=None, photo_id:Optional[int]=None, need_likes:Optional[bool]=None, start_comment_id:Optional[int]=None, offset:Optional[int]=None, count:Optional[int]=None, sort:Optional[str]=None, access_key:Optional[str]=None, extended:Optional[bool]=None, fields:Optional[list]=None) -> PhotosGetCommentsResponse| PhotosGetCommentsExtendedResponse:
		"""Returns a list of comments on a photo."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("photos.getComments", **args)
		models = [PhotosGetCommentsResponse, PhotosGetCommentsExtendedResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getMarketAlbumUploadServer(self, group_id:Optional[int]=None) -> BaseGetUploadServerResponse:
		"""Returns the server address for market album photo upload."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("photos.getMarketAlbumUploadServer", **args)
		models = [BaseGetUploadServerResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getMarketUploadServer(self, group_id:Optional[int]=None, main_photo:Optional[bool]=None, crop_x:Optional[int]=None, crop_y:Optional[int]=None, crop_width:Optional[int]=None) -> PhotosGetMarketUploadServerResponse:
		"""Returns the server address for market photo upload."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("photos.getMarketUploadServer", **args)
		models = [PhotosGetMarketUploadServerResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getMessagesUploadServer(self, peer_id:Optional[int]=None) -> PhotosGetMessagesUploadServerResponse:
		"""Returns the server address for photo upload in a private message for a user."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("photos.getMessagesUploadServer", **args)
		models = [PhotosGetMessagesUploadServerResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getNewTags(self, offset:Optional[int]=None, count:Optional[int]=None) -> PhotosGetNewTagsResponse:
		"""Returns a list of photos with tags that have not been viewed."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("photos.getNewTags", **args)
		models = [PhotosGetNewTagsResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getOwnerCoverPhotoUploadServer(self, group_id:Optional[int]=None, crop_x:Optional[int]=None, crop_y:Optional[int]=None, crop_x2:Optional[int]=None, crop_y2:Optional[int]=None) -> BaseGetUploadServerResponse:
		"""Returns the server address for owner cover upload."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("photos.getOwnerCoverPhotoUploadServer", **args)
		models = [BaseGetUploadServerResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getOwnerPhotoUploadServer(self, owner_id:Optional[int]=None) -> BaseGetUploadServerResponse:
		"""Returns an upload server address for a profile or community photo."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("photos.getOwnerPhotoUploadServer", **args)
		models = [BaseGetUploadServerResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getTags(self, owner_id:Optional[int]=None, photo_id:Optional[int]=None, access_key:Optional[str]=None) -> PhotosGetTagsResponse:
		"""Returns a list of tags on a photo."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("photos.getTags", **args)
		models = [PhotosGetTagsResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getUploadServer(self, album_id:Optional[int]=None, group_id:Optional[int]=None) -> PhotosGetUploadServerResponse:
		"""Returns the server address for photo upload."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("photos.getUploadServer", **args)
		models = [PhotosGetUploadServerResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getUserPhotos(self, user_id:Optional[int]=None, offset:Optional[int]=None, count:Optional[int]=None, extended:Optional[bool]=None, sort:Optional[str]=None) -> PhotosGetUserPhotosResponse:
		"""Returns a list of photos in which a user is tagged."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("photos.getUserPhotos", **args)
		models = [PhotosGetUserPhotosResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getWallUploadServer(self, group_id:Optional[int]=None) -> PhotosGetWallUploadServerResponse:
		"""Returns the server address for photo upload onto a user's wall."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("photos.getWallUploadServer", **args)
		models = [PhotosGetWallUploadServerResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def makeCover(self, owner_id:Optional[int]=None, photo_id:Optional[int]=None, album_id:Optional[int]=None) -> BaseOkResponse:
		"""Makes a photo into an album cover."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("photos.makeCover", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def move(self, owner_id:Optional[int]=None, target_album_id:Optional[int]=None, photo_ids:Optional[int]=None) -> BaseOkResponse:
		"""Moves a photo from one album to another."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("photos.move", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def putTag(self, owner_id:Optional[int]=None, photo_id:Optional[int]=None, user_id:Optional[int]=None, x:Optional[int]=None, y:Optional[int]=None, x2:Optional[int]=None, y2:Optional[int]=None) -> PhotosPutTagResponse:
		"""Adds a tag on the photo."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("photos.putTag", **args)
		models = [PhotosPutTagResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def removeTag(self, owner_id:Optional[int]=None, photo_id:Optional[int]=None, tag_id:Optional[int]=None) -> BaseOkResponse:
		"""Removes a tag from a photo."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("photos.removeTag", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def reorderAlbums(self, owner_id:Optional[int]=None, album_id:Optional[int]=None, before:Optional[int]=None, after:Optional[int]=None) -> BaseOkResponse:
		"""Reorders the album in the list of user albums."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("photos.reorderAlbums", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def reorderPhotos(self, owner_id:Optional[int]=None, photo_id:Optional[int]=None, before:Optional[int]=None, after:Optional[int]=None) -> BaseOkResponse:
		"""Reorders the photo in the list of photos of the user album."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("photos.reorderPhotos", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def report(self, owner_id:Optional[int]=None, photo_id:Optional[int]=None, reason:Optional[int]=None) -> BaseOkResponse:
		"""Reports (submits a complaint about) a photo."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("photos.report", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def reportComment(self, owner_id:Optional[int]=None, comment_id:Optional[int]=None, reason:Optional[int]=None) -> BaseOkResponse:
		"""Reports (submits a complaint about) a comment on a photo."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("photos.reportComment", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def restore(self, owner_id:Optional[int]=None, photo_id:Optional[int]=None) -> BaseOkResponse:
		"""Restores a deleted photo."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("photos.restore", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def restoreComment(self, owner_id:Optional[int]=None, comment_id:Optional[int]=None) -> PhotosRestoreCommentResponse:
		"""Restores a deleted comment on a photo."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("photos.restoreComment", **args)
		models = [PhotosRestoreCommentResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def save(self, album_id:Optional[int]=None, group_id:Optional[int]=None, server:Optional[int]=None, photos_list:Optional[str]=None, hash:Optional[str]=None, latitude:Optional[int]=None, longitude:Optional[int]=None, caption:Optional[str]=None) -> PhotosSaveResponse:
		"""Saves photos after successful uploading."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("photos.save", **args)
		models = [PhotosSaveResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def saveMarketAlbumPhoto(self, group_id:Optional[int]=None, photo:Optional[str]=None, server:Optional[int]=None, hash:Optional[str]=None) -> PhotosSaveMarketAlbumPhotoResponse:
		"""Saves market album photos after successful uploading."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("photos.saveMarketAlbumPhoto", **args)
		models = [PhotosSaveMarketAlbumPhotoResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def saveMarketPhoto(self, group_id:Optional[int]=None, photo:Optional[str]=None, server:Optional[int]=None, hash:Optional[str]=None, crop_data:Optional[str]=None, crop_hash:Optional[str]=None) -> PhotosSaveMarketPhotoResponse:
		"""Saves market photos after successful uploading."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("photos.saveMarketPhoto", **args)
		models = [PhotosSaveMarketPhotoResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def saveMessagesPhoto(self, photo:Optional[str]=None, server:Optional[int]=None, hash:Optional[str]=None) -> PhotosSaveMessagesPhotoResponse:
		"""Saves a photo after being successfully uploaded. URL obtained with [vk.com/dev/photos.getMessagesUploadServer|photos.getMessagesUploadServer] method."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("photos.saveMessagesPhoto", **args)
		models = [PhotosSaveMessagesPhotoResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def saveOwnerCoverPhoto(self, hash:Optional[str]=None, photo:Optional[str]=None) -> PhotosSaveOwnerCoverPhotoResponse:
		"""Saves cover photo after successful uploading."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("photos.saveOwnerCoverPhoto", **args)
		models = [PhotosSaveOwnerCoverPhotoResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def saveOwnerPhoto(self, server:Optional[str]=None, hash:Optional[str]=None, photo:Optional[str]=None) -> PhotosSaveOwnerPhotoResponse:
		"""Saves a profile or community photo. Upload URL can be got with the [vk.com/dev/photos.getOwnerPhotoUploadServer|photos.getOwnerPhotoUploadServer] method."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("photos.saveOwnerPhoto", **args)
		models = [PhotosSaveOwnerPhotoResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def saveWallPhoto(self, user_id:Optional[int]=None, group_id:Optional[int]=None, photo:Optional[str]=None, server:Optional[int]=None, hash:Optional[str]=None, latitude:Optional[int]=None, longitude:Optional[int]=None, caption:Optional[str]=None) -> PhotosSaveWallPhotoResponse:
		"""Saves a photo to a user's or community's wall after being uploaded."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("photos.saveWallPhoto", **args)
		models = [PhotosSaveWallPhotoResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def search(self, q:Optional[str]=None, lat:Optional[int]=None, long:Optional[int]=None, start_time:Optional[int]=None, end_time:Optional[int]=None, sort:Optional[int]=None, offset:Optional[int]=None, count:Optional[int]=None, radius:Optional[int]=None) -> PhotosSearchResponse:
		"""Returns a list of photos."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("photos.search", **args)
		models = [PhotosSearchResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)



class Podcasts(BaseMethod):
	def __init__(self, vk):
		super().__init__(vk)

	async def searchPodcast(self, search_string:Optional[str]=None, offset:Optional[int]=None, count:Optional[int]=None) -> PodcastsSearchPodcastResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("podcasts.searchPodcast", **args)
		models = [PodcastsSearchPodcastResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)



class Polls(BaseMethod):
	def __init__(self, vk):
		super().__init__(vk)

	async def addVote(self, owner_id:Optional[int]=None, poll_id:Optional[int]=None, answer_ids:Optional[list]=None, is_board:Optional[bool]=None) -> PollsAddVoteResponse:
		"""Adds the current user's vote to the selected answer in the poll."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("polls.addVote", **args)
		models = [PollsAddVoteResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def create(self, question:Optional[str]=None, is_anonymous:Optional[bool]=None, is_multiple:Optional[bool]=None, end_date:Optional[int]=None, owner_id:Optional[int]=None, app_id:Optional[int]=None, add_answers:Optional[str]=None, photo_id:Optional[int]=None, background_id:Optional[str]=None, disable_unvote:Optional[bool]=None) -> PollsCreateResponse:
		"""Creates polls that can be attached to the users' or communities' posts."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("polls.create", **args)
		models = [PollsCreateResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def deleteVote(self, owner_id:Optional[int]=None, poll_id:Optional[int]=None, answer_id:Optional[int]=None, is_board:Optional[bool]=None) -> PollsDeleteVoteResponse:
		"""Deletes the current user's vote from the selected answer in the poll."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("polls.deleteVote", **args)
		models = [PollsDeleteVoteResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def edit(self, owner_id:Optional[int]=None, poll_id:Optional[int]=None, question:Optional[str]=None, add_answers:Optional[str]=None, edit_answers:Optional[str]=None, delete_answers:Optional[str]=None, end_date:Optional[int]=None, photo_id:Optional[int]=None, background_id:Optional[str]=None) -> BaseOkResponse:
		"""Edits created polls"""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("polls.edit", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getBackgrounds(self) -> PollsGetBackgroundsResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("polls.getBackgrounds", **args)
		models = [PollsGetBackgroundsResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getById(self, owner_id:Optional[int]=None, is_board:Optional[bool]=None, poll_id:Optional[int]=None, extended:Optional[bool]=None, friends_count:Optional[int]=None, fields:Optional[list]=None, name_case:Optional[str]=None) -> PollsGetByIdResponse:
		"""Returns detailed information about a poll by its ID."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("polls.getById", **args)
		models = [PollsGetByIdResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getPhotoUploadServer(self, owner_id:Optional[int]=None) -> BaseGetUploadServerResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("polls.getPhotoUploadServer", **args)
		models = [BaseGetUploadServerResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getVoters(self, owner_id:Optional[int]=None, poll_id:Optional[int]=None, answer_ids:Optional[list]=None, is_board:Optional[bool]=None, friends_only:Optional[bool]=None, offset:Optional[int]=None, count:Optional[int]=None, fields:Optional[list]=None, name_case:Optional[str]=None) -> PollsGetVotersResponse:
		"""Returns a list of IDs of users who selected specific answers in the poll."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("polls.getVoters", **args)
		models = [PollsGetVotersResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def savePhoto(self, photo:Optional[str]=None, hash:Optional[str]=None) -> PollsSavePhotoResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("polls.savePhoto", **args)
		models = [PollsSavePhotoResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)



class Prettycards(BaseMethod):
	def __init__(self, vk):
		super().__init__(vk)

	async def create(self, owner_id:Optional[int]=None, photo:Optional[str]=None, title:Optional[str]=None, link:Optional[str]=None, price:Optional[str]=None, price_old:Optional[str]=None, button:Optional[str]=None) -> PrettyCardsCreateResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("prettycards.create", **args)
		models = [PrettyCardsCreateResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def delete(self, owner_id:Optional[int]=None, card_id:Optional[int]=None) -> PrettyCardsDeleteResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("prettycards.delete", **args)
		models = [PrettyCardsDeleteResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def edit(self, owner_id:Optional[int]=None, card_id:Optional[int]=None, photo:Optional[str]=None, title:Optional[str]=None, link:Optional[str]=None, price:Optional[str]=None, price_old:Optional[str]=None, button:Optional[str]=None) -> PrettyCardsEditResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("prettycards.edit", **args)
		models = [PrettyCardsEditResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def get(self, owner_id:Optional[int]=None, offset:Optional[int]=None, count:Optional[int]=None) -> PrettyCardsGetResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("prettycards.get", **args)
		models = [PrettyCardsGetResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getById(self, owner_id:Optional[int]=None, card_ids:Optional[list]=None) -> PrettyCardsGetByIdResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("prettycards.getById", **args)
		models = [PrettyCardsGetByIdResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getUploadURL(self) -> PrettyCardsGetUploadURLResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("prettycards.getUploadURL", **args)
		models = [PrettyCardsGetUploadURLResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)



class Search(BaseMethod):
	def __init__(self, vk):
		super().__init__(vk)

	async def getHints(self, q:Optional[str]=None, offset:Optional[int]=None, limit:Optional[int]=None, filters:Optional[list]=None, fields:Optional[list]=None, search_global:Optional[bool]=None) -> SearchGetHintsResponse:
		"""Allows the programmer to do a quick search for any substring."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("search.getHints", **args)
		models = [SearchGetHintsResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)



class Secure(BaseMethod):
	def __init__(self, vk):
		super().__init__(vk)

	async def addAppEvent(self, user_id:Optional[int]=None, activity_id:Optional[int]=None, value:Optional[int]=None) -> BaseOkResponse:
		"""Adds user activity information to an application"""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("secure.addAppEvent", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def checkToken(self, token:Optional[str]=None, ip:Optional[str]=None) -> SecureCheckTokenResponse:
		"""Checks the user authentication in 'IFrame' and 'Flash' apps using the 'access_token' parameter."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("secure.checkToken", **args)
		models = [SecureCheckTokenResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getAppBalance(self) -> SecureGetAppBalanceResponse:
		"""Returns payment balance of the application in hundredth of a vote."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("secure.getAppBalance", **args)
		models = [SecureGetAppBalanceResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getSMSHistory(self, user_id:Optional[int]=None, date_from:Optional[int]=None, date_to:Optional[int]=None, limit:Optional[int]=None) -> SecureGetSMSHistoryResponse:
		"""Shows a list of SMS notifications sent by the application using [vk.com/dev/secure.sendSMSNotification|secure.sendSMSNotification] method."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("secure.getSMSHistory", **args)
		models = [SecureGetSMSHistoryResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getTransactionsHistory(self, type:Optional[int]=None, uid_from:Optional[int]=None, uid_to:Optional[int]=None, date_from:Optional[int]=None, date_to:Optional[int]=None, limit:Optional[int]=None) -> SecureGetTransactionsHistoryResponse:
		"""Shows history of votes transaction between users and the application."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("secure.getTransactionsHistory", **args)
		models = [SecureGetTransactionsHistoryResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getUserLevel(self, user_ids:Optional[list]=None) -> SecureGetUserLevelResponse:
		"""Returns one of the previously set game levels of one or more users in the application."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("secure.getUserLevel", **args)
		models = [SecureGetUserLevelResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def giveEventSticker(self, user_ids:Optional[list]=None, achievement_id:Optional[int]=None) -> SecureGiveEventStickerResponse:
		"""Opens the game achievement and gives the user a sticker"""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("secure.giveEventSticker", **args)
		models = [SecureGiveEventStickerResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def sendNotification(self, user_ids:Optional[list]=None, user_id:Optional[int]=None, message:Optional[str]=None) -> SecureSendNotificationResponse:
		"""Sends notification to the user."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("secure.sendNotification", **args)
		models = [SecureSendNotificationResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def sendSMSNotification(self, user_id:Optional[int]=None, message:Optional[str]=None) -> BaseOkResponse:
		"""Sends 'SMS' notification to a user's mobile device."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("secure.sendSMSNotification", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def setCounter(self, counters:Optional[list]=None, user_id:Optional[int]=None, counter:Optional[int]=None, increment:Optional[bool]=None) -> BaseBoolResponse| SecureSetCounterArrayResponse:
		"""Sets a counter which is shown to the user in bold in the left menu."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("secure.setCounter", **args)
		models = [BaseBoolResponse, SecureSetCounterArrayResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)



class Stats(BaseMethod):
	def __init__(self, vk):
		super().__init__(vk)

	async def get(self, group_id:Optional[int]=None, app_id:Optional[int]=None, timestamp_from:Optional[int]=None, timestamp_to:Optional[int]=None, interval:Optional[str]=None, intervals_count:Optional[int]=None, filters:Optional[list]=None, stats_groups:Optional[list]=None, extended:Optional[bool]=None) -> StatsGetResponse:
		"""Returns statistics of a community or an application."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("stats.get", **args)
		models = [StatsGetResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getPostReach(self, owner_id:Optional[str]=None, post_ids:Optional[list]=None) -> StatsGetPostReachResponse:
		"""Returns stats for a wall post."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("stats.getPostReach", **args)
		models = [StatsGetPostReachResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def trackVisitor(self) -> BaseOkResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("stats.trackVisitor", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)



class Status(BaseMethod):
	def __init__(self, vk):
		super().__init__(vk)

	async def get(self, user_id:Optional[int]=None, group_id:Optional[int]=None) -> StatusGetResponse:
		"""Returns data required to show the status of a user or community."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("status.get", **args)
		models = [StatusGetResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def set(self, text:Optional[str]=None, group_id:Optional[int]=None) -> BaseOkResponse:
		"""Sets a new status for the current user."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("status.set", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)



class Storage(BaseMethod):
	def __init__(self, vk):
		super().__init__(vk)

	async def get(self, key:Optional[str]=None, keys:Optional[list]=None, user_id:Optional[int]=None) -> StorageGetResponse:
		"""Returns a value of variable with the name set by key parameter."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("storage.get", **args)
		models = [StorageGetResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getKeys(self, user_id:Optional[int]=None, offset:Optional[int]=None, count:Optional[int]=None) -> StorageGetKeysResponse:
		"""Returns the names of all variables."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("storage.getKeys", **args)
		models = [StorageGetKeysResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def set(self, key:Optional[str]=None, value:Optional[str]=None, user_id:Optional[int]=None) -> BaseOkResponse:
		"""Saves a value of variable with the name set by 'key' parameter."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("storage.set", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)



class Store(BaseMethod):
	def __init__(self, vk):
		super().__init__(vk)

	async def addStickersToFavorite(self, sticker_ids:Optional[list]=None) -> BaseOkResponse:
		"""Adds given sticker IDs to the list of user's favorite stickers"""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("store.addStickersToFavorite", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getFavoriteStickers(self) -> StoreGetFavoriteStickersResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("store.getFavoriteStickers", **args)
		models = [StoreGetFavoriteStickersResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getProducts(self, type:Optional[str]=None, merchant:Optional[str]=None, section:Optional[str]=None, product_ids:Optional[list]=None, filters:Optional[list]=None, extended:Optional[bool]=None) -> StoreGetProductsResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("store.getProducts", **args)
		models = [StoreGetProductsResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getStickersKeywords(self, stickers_ids:Optional[list]=None, products_ids:Optional[list]=None, aliases:Optional[bool]=None, all_products:Optional[bool]=None, need_stickers:Optional[bool]=None) -> StoreGetStickersKeywordsResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("store.getStickersKeywords", **args)
		models = [StoreGetStickersKeywordsResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def removeStickersFromFavorite(self, sticker_ids:Optional[list]=None) -> BaseOkResponse:
		"""Removes given sticker IDs from the list of user's favorite stickers"""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("store.removeStickersFromFavorite", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)



class Stories(BaseMethod):
	def __init__(self, vk):
		super().__init__(vk)

	async def banOwner(self, owners_ids:Optional[list]=None) -> BaseOkResponse:
		"""Allows to hide stories from chosen sources from current user's feed."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("stories.banOwner", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def delete(self, owner_id:Optional[int]=None, story_id:Optional[int]=None, stories:Optional[list]=None) -> BaseOkResponse:
		"""Allows to delete story."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("stories.delete", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def get(self, owner_id:Optional[int]=None, extended:Optional[bool]=None, fields:Optional[list]=None) -> StoriesGetV5113Response:
		"""Returns stories available for current user."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("stories.get", **args)
		models = [StoriesGetV5113Response]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getBanned(self, extended:Optional[bool]=None, fields:Optional[list]=None) -> StoriesGetBannedResponse| StoriesGetBannedExtendedResponse:
		"""Returns list of sources hidden from current user's feed."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("stories.getBanned", **args)
		models = [StoriesGetBannedResponse, StoriesGetBannedExtendedResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getById(self, stories:Optional[list]=None, extended:Optional[bool]=None, fields:Optional[list]=None) -> StoriesGetByIdExtendedResponse:
		"""Returns story by its ID."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("stories.getById", **args)
		models = [StoriesGetByIdExtendedResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getPhotoUploadServer(self, add_to_news:Optional[bool]=None, user_ids:Optional[list]=None, reply_to_story:Optional[str]=None, link_text:Optional[str]=None, link_url:Optional[str]=None, group_id:Optional[int]=None, clickable_stickers:Optional[str]=None) -> StoriesGetPhotoUploadServerResponse:
		"""Returns URL for uploading a story with photo."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("stories.getPhotoUploadServer", **args)
		models = [StoriesGetPhotoUploadServerResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getReplies(self, owner_id:Optional[int]=None, story_id:Optional[int]=None, access_key:Optional[str]=None, extended:Optional[bool]=None, fields:Optional[list]=None) -> StoriesGetV5113Response:
		"""Returns replies to the story."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("stories.getReplies", **args)
		models = [StoriesGetV5113Response]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getStats(self, owner_id:Optional[int]=None, story_id:Optional[int]=None) -> StoriesGetStatsResponse:
		"""Returns stories available for current user."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("stories.getStats", **args)
		models = [StoriesGetStatsResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getVideoUploadServer(self, add_to_news:Optional[bool]=None, user_ids:Optional[list]=None, reply_to_story:Optional[str]=None, link_text:Optional[str]=None, link_url:Optional[str]=None, group_id:Optional[int]=None, clickable_stickers:Optional[str]=None) -> StoriesGetVideoUploadServerResponse:
		"""Allows to receive URL for uploading story with video."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("stories.getVideoUploadServer", **args)
		models = [StoriesGetVideoUploadServerResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getViewers(self, owner_id:Optional[int]=None, story_id:Optional[int]=None, count:Optional[int]=None, offset:Optional[int]=None, extended:Optional[bool]=None, fields:Optional[list]=None) -> StoriesGetViewersExtendedV5115Response| StoriesGetViewersExtendedV5115Response:
		"""Returns a list of story viewers."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("stories.getViewers", **args)
		models = [StoriesGetViewersExtendedV5115Response, StoriesGetViewersExtendedV5115Response]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def hideAllReplies(self, owner_id:Optional[int]=None, group_id:Optional[int]=None) -> BaseOkResponse:
		"""Hides all replies in the last 24 hours from the user to current user's stories."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("stories.hideAllReplies", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def hideReply(self, owner_id:Optional[int]=None, story_id:Optional[int]=None) -> BaseOkResponse:
		"""Hides the reply to the current user's story."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("stories.hideReply", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def save(self, upload_results:Optional[list]=None, extended:Optional[bool]=None, fields:Optional[list]=None) -> StoriesSaveResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("stories.save", **args)
		models = [StoriesSaveResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def search(self, q:Optional[str]=None, place_id:Optional[int]=None, latitude:Optional[int]=None, longitude:Optional[int]=None, radius:Optional[int]=None, mentioned_id:Optional[int]=None, count:Optional[int]=None, extended:Optional[bool]=None, fields:Optional[list]=None) -> StoriesGetV5113Response:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("stories.search", **args)
		models = [StoriesGetV5113Response]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def sendInteraction(self, access_key:Optional[str]=None, message:Optional[str]=None, is_broadcast:Optional[bool]=None, is_anonymous:Optional[bool]=None, unseen_marker:Optional[bool]=None) -> BaseOkResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("stories.sendInteraction", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def unbanOwner(self, owners_ids:Optional[list]=None) -> BaseOkResponse:
		"""Allows to show stories from hidden sources in current user's feed."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("stories.unbanOwner", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)



class Streaming(BaseMethod):
	def __init__(self, vk):
		super().__init__(vk)

	async def getServerUrl(self) -> StreamingGetServerUrlResponse:
		"""Allows to receive data for the connection to Streaming API."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("streaming.getServerUrl", **args)
		models = [StreamingGetServerUrlResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def setSettings(self, monthly_tier:Optional[str]=None) -> BaseOkResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("streaming.setSettings", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)



class Users(BaseMethod):
	def __init__(self, vk):
		super().__init__(vk)

	async def get(self, user_ids:Optional[list]=None, fields:Optional[list]=None, name_case:Optional[str]=None) -> UsersGetResponse:
		"""Returns detailed information on users."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("users.get", **args)
		models = [UsersGetResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getFollowers(self, user_id:Optional[int]=None, offset:Optional[int]=None, count:Optional[int]=None, fields:Optional[list]=None, name_case:Optional[str]=None) -> UsersGetFollowersResponse| UsersGetFollowersFieldsResponse:
		"""Returns a list of IDs of followers of the user in question, sorted by date added, most recent first."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("users.getFollowers", **args)
		models = [UsersGetFollowersResponse, UsersGetFollowersFieldsResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getSubscriptions(self, user_id:Optional[int]=None, extended:Optional[bool]=None, offset:Optional[int]=None, count:Optional[int]=None, fields:Optional[list]=None) -> UsersGetSubscriptionsResponse| UsersGetSubscriptionsExtendedResponse:
		"""Returns a list of IDs of users and communities followed by the user."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("users.getSubscriptions", **args)
		models = [UsersGetSubscriptionsResponse, UsersGetSubscriptionsExtendedResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def report(self, user_id:Optional[int]=None, type:Optional[str]=None, comment:Optional[str]=None) -> BaseOkResponse:
		"""Reports (submits a complain about) a user."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("users.report", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def search(self, q:Optional[str]=None, sort:Optional[int]=None, offset:Optional[int]=None, count:Optional[int]=None, fields:Optional[list]=None, city:Optional[int]=None, country:Optional[int]=None, hometown:Optional[str]=None, university_country:Optional[int]=None, university:Optional[int]=None, university_year:Optional[int]=None, university_faculty:Optional[int]=None, university_chair:Optional[int]=None, sex:Optional[int]=None, status:Optional[int]=None, age_from:Optional[int]=None, age_to:Optional[int]=None, birth_day:Optional[int]=None, birth_month:Optional[int]=None, birth_year:Optional[int]=None, online:Optional[bool]=None, has_photo:Optional[bool]=None, school_country:Optional[int]=None, school_city:Optional[int]=None, school_class:Optional[int]=None, school:Optional[int]=None, school_year:Optional[int]=None, religion:Optional[str]=None, company:Optional[str]=None, position:Optional[str]=None, group_id:Optional[int]=None, from_list:Optional[list]=None) -> UsersSearchResponse:
		"""Returns a list of users matching the search criteria."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("users.search", **args)
		models = [UsersSearchResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)



class Utils(BaseMethod):
	def __init__(self, vk):
		super().__init__(vk)

	async def checkLink(self, url:Optional[str]=None) -> UtilsCheckLinkResponse:
		"""Checks whether a link is blocked in VK."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("utils.checkLink", **args)
		models = [UtilsCheckLinkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def deleteFromLastShortened(self, key:Optional[str]=None) -> BaseOkResponse:
		"""Deletes shortened link from user's list."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("utils.deleteFromLastShortened", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getLastShortenedLinks(self, count:Optional[int]=None, offset:Optional[int]=None) -> UtilsGetLastShortenedLinksResponse:
		"""Returns a list of user's shortened links."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("utils.getLastShortenedLinks", **args)
		models = [UtilsGetLastShortenedLinksResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getLinkStats(self, key:Optional[str]=None, source:Optional[str]=None, access_key:Optional[str]=None, interval:Optional[str]=None, intervals_count:Optional[int]=None, extended:Optional[bool]=None) -> UtilsGetLinkStatsResponse| UtilsGetLinkStatsExtendedResponse:
		"""Returns stats data for shortened link."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("utils.getLinkStats", **args)
		models = [UtilsGetLinkStatsResponse, UtilsGetLinkStatsExtendedResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getServerTime(self) -> UtilsGetServerTimeResponse:
		"""Returns the current time of the VK server."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("utils.getServerTime", **args)
		models = [UtilsGetServerTimeResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getShortLink(self, url:Optional[str]=None, private:Optional[bool]=None) -> UtilsGetShortLinkResponse:
		"""Allows to receive a link shortened via vk.cc."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("utils.getShortLink", **args)
		models = [UtilsGetShortLinkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def resolveScreenName(self, screen_name:Optional[str]=None) -> UtilsResolveScreenNameResponse:
		"""Detects a type of object (e.g., user, community, application) and its ID by screen name."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("utils.resolveScreenName", **args)
		models = [UtilsResolveScreenNameResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)



class Video(BaseMethod):
	def __init__(self, vk):
		super().__init__(vk)

	async def add(self, target_id:Optional[int]=None, video_id:Optional[int]=None, owner_id:Optional[int]=None) -> BaseOkResponse:
		"""Adds a video to a user or community page."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("video.add", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def addAlbum(self, group_id:Optional[int]=None, title:Optional[str]=None, privacy:Optional[list]=None) -> VideoAddAlbumResponse:
		"""Creates an empty album for videos."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("video.addAlbum", **args)
		models = [VideoAddAlbumResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def addToAlbum(self, target_id:Optional[int]=None, album_id:Optional[int]=None, album_ids:Optional[list]=None, owner_id:Optional[int]=None, video_id:Optional[int]=None) -> BaseOkResponse| VideoChangeVideoAlbumsResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("video.addToAlbum", **args)
		models = [BaseOkResponse, VideoChangeVideoAlbumsResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def createComment(self, owner_id:Optional[int]=None, video_id:Optional[int]=None, message:Optional[str]=None, attachments:Optional[str]=None, from_group:Optional[bool]=None, reply_to_comment:Optional[int]=None, sticker_id:Optional[int]=None, guid:Optional[str]=None) -> VideoCreateCommentResponse:
		"""Adds a new comment on a video."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("video.createComment", **args)
		models = [VideoCreateCommentResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def delete(self, video_id:Optional[int]=None, owner_id:Optional[int]=None, target_id:Optional[int]=None) -> BaseOkResponse:
		"""Deletes a video from a user or community page."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("video.delete", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def deleteAlbum(self, group_id:Optional[int]=None, album_id:Optional[int]=None) -> BaseOkResponse:
		"""Deletes a video album."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("video.deleteAlbum", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def deleteComment(self, owner_id:Optional[int]=None, comment_id:Optional[int]=None) -> BaseOkResponse:
		"""Deletes a comment on a video."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("video.deleteComment", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def edit(self, owner_id:Optional[int]=None, video_id:Optional[int]=None, name:Optional[str]=None, desc:Optional[str]=None, privacy_view:Optional[list]=None, privacy_comment:Optional[list]=None, no_comments:Optional[bool]=None, repeat:Optional[bool]=None) -> BaseOkResponse:
		"""Edits information about a video on a user or community page."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("video.edit", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def editAlbum(self, group_id:Optional[int]=None, album_id:Optional[int]=None, title:Optional[str]=None, privacy:Optional[list]=None) -> BaseOkResponse:
		"""Edits the title of a video album."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("video.editAlbum", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def editComment(self, owner_id:Optional[int]=None, comment_id:Optional[int]=None, message:Optional[str]=None, attachments:Optional[str]=None) -> BaseOkResponse:
		"""Edits the text of a comment on a video."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("video.editComment", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def get(self, owner_id:Optional[int]=None, videos:Optional[list]=None, album_id:Optional[int]=None, count:Optional[int]=None, offset:Optional[int]=None, extended:Optional[bool]=None, fields:Optional[list]=None) -> VideoGetResponse:
		"""Returns detailed information about videos."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("video.get", **args)
		models = [VideoGetResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getAlbumById(self, owner_id:Optional[int]=None, album_id:Optional[int]=None) -> VideoGetAlbumByIdResponse:
		"""Returns video album info"""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("video.getAlbumById", **args)
		models = [VideoGetAlbumByIdResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getAlbums(self, owner_id:Optional[int]=None, offset:Optional[int]=None, count:Optional[int]=None, extended:Optional[bool]=None, need_system:Optional[bool]=None) -> VideoGetAlbumsResponse| VideoGetAlbumsExtendedResponse:
		"""Returns a list of video albums owned by a user or community."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("video.getAlbums", **args)
		models = [VideoGetAlbumsResponse, VideoGetAlbumsExtendedResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getAlbumsByVideo(self, target_id:Optional[int]=None, owner_id:Optional[int]=None, video_id:Optional[int]=None, extended:Optional[bool]=None) -> VideoGetAlbumsByVideoResponse| VideoGetAlbumsByVideoExtendedResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("video.getAlbumsByVideo", **args)
		models = [VideoGetAlbumsByVideoResponse, VideoGetAlbumsByVideoExtendedResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getComments(self, owner_id:Optional[int]=None, video_id:Optional[int]=None, need_likes:Optional[bool]=None, start_comment_id:Optional[int]=None, offset:Optional[int]=None, count:Optional[int]=None, sort:Optional[str]=None, extended:Optional[bool]=None, fields:Optional[list]=None) -> VideoGetCommentsResponse| VideoGetCommentsExtendedResponse:
		"""Returns a list of comments on a video."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("video.getComments", **args)
		models = [VideoGetCommentsResponse, VideoGetCommentsExtendedResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def removeFromAlbum(self, target_id:Optional[int]=None, album_id:Optional[int]=None, album_ids:Optional[list]=None, owner_id:Optional[int]=None, video_id:Optional[int]=None) -> BaseOkResponse| VideoChangeVideoAlbumsResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("video.removeFromAlbum", **args)
		models = [BaseOkResponse, VideoChangeVideoAlbumsResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def reorderAlbums(self, owner_id:Optional[int]=None, album_id:Optional[int]=None, before:Optional[int]=None, after:Optional[int]=None) -> BaseOkResponse:
		"""Reorders the album in the list of user video albums."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("video.reorderAlbums", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def reorderVideos(self, target_id:Optional[int]=None, album_id:Optional[int]=None, owner_id:Optional[int]=None, video_id:Optional[int]=None, before_owner_id:Optional[int]=None, before_video_id:Optional[int]=None, after_owner_id:Optional[int]=None, after_video_id:Optional[int]=None) -> BaseOkResponse:
		"""Reorders the video in the video album."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("video.reorderVideos", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def report(self, owner_id:Optional[int]=None, video_id:Optional[int]=None, reason:Optional[int]=None, comment:Optional[str]=None, search_query:Optional[str]=None) -> BaseOkResponse:
		"""Reports (submits a complaint about) a video."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("video.report", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def reportComment(self, owner_id:Optional[int]=None, comment_id:Optional[int]=None, reason:Optional[int]=None) -> BaseOkResponse:
		"""Reports (submits a complaint about) a comment on a video."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("video.reportComment", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def restore(self, video_id:Optional[int]=None, owner_id:Optional[int]=None) -> BaseOkResponse:
		"""Restores a previously deleted video."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("video.restore", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def restoreComment(self, owner_id:Optional[int]=None, comment_id:Optional[int]=None) -> VideoRestoreCommentResponse:
		"""Restores a previously deleted comment on a video."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("video.restoreComment", **args)
		models = [VideoRestoreCommentResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def save(self, name:Optional[str]=None, description:Optional[str]=None, is_private:Optional[bool]=None, wallpost:Optional[bool]=None, link:Optional[str]=None, group_id:Optional[int]=None, album_id:Optional[int]=None, privacy_view:Optional[list]=None, privacy_comment:Optional[list]=None, no_comments:Optional[bool]=None, repeat:Optional[bool]=None, compression:Optional[bool]=None) -> VideoSaveResponse:
		"""Returns a server address (required for upload) and video data."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("video.save", **args)
		models = [VideoSaveResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def search(self, q:Optional[str]=None, sort:Optional[int]=None, hd:Optional[int]=None, adult:Optional[bool]=None, live:Optional[bool]=None, filters:Optional[list]=None, search_own:Optional[bool]=None, offset:Optional[int]=None, longer:Optional[int]=None, shorter:Optional[int]=None, count:Optional[int]=None, extended:Optional[bool]=None) -> VideoSearchResponse| VideoSearchExtendedResponse:
		"""Returns a list of videos under the set search criterion."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("video.search", **args)
		models = [VideoSearchResponse, VideoSearchExtendedResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)



class Wall(BaseMethod):
	def __init__(self, vk):
		super().__init__(vk)

	async def checkCopyrightLink(self, link:Optional[str]=None) -> BaseBoolResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("wall.checkCopyrightLink", **args)
		models = [BaseBoolResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def closeComments(self, owner_id:Optional[int]=None, post_id:Optional[int]=None) -> BaseBoolResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("wall.closeComments", **args)
		models = [BaseBoolResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def createComment(self, owner_id:Optional[int]=None, post_id:Optional[int]=None, from_group:Optional[int]=None, message:Optional[str]=None, reply_to_comment:Optional[int]=None, attachments:Optional[str]=None, sticker_id:Optional[int]=None, guid:Optional[str]=None) -> WallCreateCommentResponse:
		"""Adds a comment to a post on a user wall or community wall."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("wall.createComment", **args)
		models = [WallCreateCommentResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def delete(self, owner_id:Optional[int]=None, post_id:Optional[int]=None) -> BaseOkResponse:
		"""Deletes a post from a user wall or community wall."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("wall.delete", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def deleteComment(self, owner_id:Optional[int]=None, comment_id:Optional[int]=None) -> BaseOkResponse:
		"""Deletes a comment on a post on a user wall or community wall."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("wall.deleteComment", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def edit(self, owner_id:Optional[int]=None, post_id:Optional[int]=None, friends_only:Optional[bool]=None, message:Optional[str]=None, attachments:Optional[str]=None, services:Optional[str]=None, signed:Optional[bool]=None, publish_date:Optional[int]=None, lat:Optional[int]=None, long:Optional[int]=None, place_id:Optional[int]=None, mark_as_ads:Optional[bool]=None, close_comments:Optional[bool]=None, donut_paid_duration:Optional[int]=None, poster_bkg_id:Optional[int]=None, poster_bkg_owner_id:Optional[int]=None, poster_bkg_access_hash:Optional[str]=None, copyright:Optional[str]=None, topic_id:Optional[int]=None) -> WallEditResponse:
		"""Edits a post on a user wall or community wall."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("wall.edit", **args)
		models = [WallEditResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def editAdsStealth(self, owner_id:Optional[int]=None, post_id:Optional[int]=None, message:Optional[str]=None, attachments:Optional[str]=None, signed:Optional[bool]=None, lat:Optional[int]=None, long:Optional[int]=None, place_id:Optional[int]=None, link_button:Optional[str]=None, link_title:Optional[str]=None, link_image:Optional[str]=None, link_video:Optional[str]=None) -> BaseOkResponse:
		"""Allows to edit hidden post."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("wall.editAdsStealth", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def editComment(self, owner_id:Optional[int]=None, comment_id:Optional[int]=None, message:Optional[str]=None, attachments:Optional[str]=None) -> BaseOkResponse:
		"""Edits a comment on a user wall or community wall."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("wall.editComment", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def get(self, owner_id:Optional[int]=None, domain:Optional[str]=None, offset:Optional[int]=None, count:Optional[int]=None, filter:Optional[str]=None, extended:Optional[bool]=None, fields:Optional[list]=None) -> WallGetResponse| WallGetExtendedResponse:
		"""Returns a list of posts on a user wall or community wall."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("wall.get", **args)
		models = [WallGetResponse, WallGetExtendedResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getById(self, posts:Optional[list]=None, extended:Optional[bool]=None, copy_history_depth:Optional[int]=None, fields:Optional[list]=None) -> WallGetByIdLegacyResponse| WallGetByIdExtendedResponse:
		"""Returns a list of posts from user or community walls by their IDs."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("wall.getById", **args)
		models = [WallGetByIdLegacyResponse, WallGetByIdExtendedResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getComment(self, owner_id:Optional[int]=None, comment_id:Optional[int]=None, extended:Optional[bool]=None, fields:Optional[list]=None) -> WallGetCommentResponse| WallGetCommentExtendedResponse:
		"""Returns a comment on a post on a user wall or community wall."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("wall.getComment", **args)
		models = [WallGetCommentResponse, WallGetCommentExtendedResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getComments(self, owner_id:Optional[int]=None, post_id:Optional[int]=None, need_likes:Optional[bool]=None, start_comment_id:Optional[int]=None, offset:Optional[int]=None, count:Optional[int]=None, sort:Optional[str]=None, preview_length:Optional[int]=None, extended:Optional[bool]=None, fields:Optional[list]=None, comment_id:Optional[int]=None, thread_items_count:Optional[int]=None) -> WallGetCommentsResponse| WallGetCommentsExtendedResponse:
		"""Returns a list of comments on a post on a user wall or community wall."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("wall.getComments", **args)
		models = [WallGetCommentsResponse, WallGetCommentsExtendedResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getReposts(self, owner_id:Optional[int]=None, post_id:Optional[int]=None, offset:Optional[int]=None, count:Optional[int]=None) -> WallGetRepostsResponse:
		"""Returns information about reposts of a post on user wall or community wall."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("wall.getReposts", **args)
		models = [WallGetRepostsResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def openComments(self, owner_id:Optional[int]=None, post_id:Optional[int]=None) -> BaseBoolResponse:
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("wall.openComments", **args)
		models = [BaseBoolResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def pin(self, owner_id:Optional[int]=None, post_id:Optional[int]=None) -> BaseOkResponse:
		"""Pins the post on wall."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("wall.pin", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def post(self, owner_id:Optional[int]=None, friends_only:Optional[bool]=None, from_group:Optional[bool]=None, message:Optional[str]=None, attachments:Optional[str]=None, services:Optional[str]=None, signed:Optional[bool]=None, publish_date:Optional[int]=None, lat:Optional[int]=None, long:Optional[int]=None, place_id:Optional[int]=None, post_id:Optional[int]=None, guid:Optional[str]=None, mark_as_ads:Optional[bool]=None, close_comments:Optional[bool]=None, donut_paid_duration:Optional[int]=None, mute_notifications:Optional[bool]=None, copyright:Optional[str]=None, topic_id:Optional[int]=None) -> WallPostResponse:
		"""Adds a new post on a user wall or community wall. Can also be used to publish suggested or scheduled posts."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("wall.post", **args)
		models = [WallPostResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def postAdsStealth(self, owner_id:Optional[int]=None, message:Optional[str]=None, attachments:Optional[str]=None, signed:Optional[bool]=None, lat:Optional[int]=None, long:Optional[int]=None, place_id:Optional[int]=None, guid:Optional[str]=None, link_button:Optional[str]=None, link_title:Optional[str]=None, link_image:Optional[str]=None, link_video:Optional[str]=None) -> WallPostAdsStealthResponse:
		"""Allows to create hidden post which will not be shown on the community's wall and can be used for creating an ad with type 'Community post'."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("wall.postAdsStealth", **args)
		models = [WallPostAdsStealthResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def reportComment(self, owner_id:Optional[int]=None, comment_id:Optional[int]=None, reason:Optional[int]=None) -> BaseOkResponse:
		"""Reports (submits a complaint about) a comment on a post on a user wall or community wall."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("wall.reportComment", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def reportPost(self, owner_id:Optional[int]=None, post_id:Optional[int]=None, reason:Optional[int]=None) -> BaseOkResponse:
		"""Reports (submits a complaint about) a post on a user wall or community wall."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("wall.reportPost", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def repost(self, object:Optional[str]=None, message:Optional[str]=None, group_id:Optional[int]=None, mark_as_ads:Optional[bool]=None, mute_notifications:Optional[bool]=None) -> WallRepostResponse:
		"""Reposts (copies) an object to a user wall or community wall."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("wall.repost", **args)
		models = [WallRepostResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def restore(self, owner_id:Optional[int]=None, post_id:Optional[int]=None) -> BaseOkResponse:
		"""Restores a post deleted from a user wall or community wall."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("wall.restore", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def restoreComment(self, owner_id:Optional[int]=None, comment_id:Optional[int]=None) -> BaseOkResponse:
		"""Restores a comment deleted from a user wall or community wall."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("wall.restoreComment", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def search(self, owner_id:Optional[int]=None, domain:Optional[str]=None, query:Optional[str]=None, owners_only:Optional[bool]=None, count:Optional[int]=None, offset:Optional[int]=None, extended:Optional[bool]=None, fields:Optional[list]=None) -> WallSearchResponse| WallSearchExtendedResponse:
		"""Allows to search posts on user or community walls."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("wall.search", **args)
		models = [WallSearchResponse, WallSearchExtendedResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def unpin(self, owner_id:Optional[int]=None, post_id:Optional[int]=None) -> BaseOkResponse:
		"""Unpins the post on wall."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("wall.unpin", **args)
		models = [BaseOkResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)



class Widgets(BaseMethod):
	def __init__(self, vk):
		super().__init__(vk)

	async def getComments(self, widget_api_id:Optional[int]=None, url:Optional[str]=None, page_id:Optional[str]=None, order:Optional[str]=None, fields:Optional[list]=None, offset:Optional[int]=None, count:Optional[int]=None) -> WidgetsGetCommentsResponse:
		"""Gets a list of comments for the page added through the [vk.com/dev/Comments|Comments widget]."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("widgets.getComments", **args)
		models = [WidgetsGetCommentsResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)


	async def getPages(self, widget_api_id:Optional[int]=None, order:Optional[str]=None, period:Optional[str]=None, offset:Optional[int]=None, count:Optional[int]=None) -> WidgetsGetPagesResponse:
		"""Gets a list of application/site pages where the [vk.com/dev/Comments|Comments widget] or [vk.com/dev/Like|Like widget] is installed."""
		args = locals()
		for i in ('self', '__class__'): args.pop(i)
		r = await super()._method("widgets.getPages", **args)
		models = [WidgetsGetPagesResponse]
		for m in models:
			try: return m.parse_obj(r)
			except: pass
		raise GetResponseHandlerException(r, models)



__all__ = ('Account', 'Ads', 'Adsweb', 'Appwidgets', 'Apps', 'Auth', 'Board', 'Database', 'Docs', 'Donut', 'Downloadedgames', 'Fave', 'Friends', 'Gifts', 'Groups', 'Leadforms', 'Likes', 'Market', 'Messages', 'Newsfeed', 'Notes', 'Notifications', 'Orders', 'Pages', 'Photos', 'Podcasts', 'Polls', 'Prettycards', 'Search', 'Secure', 'Stats', 'Status', 'Storage', 'Store', 'Stories', 'Streaming', 'Users', 'Utils', 'Video', 'Wall', 'Widgets')
