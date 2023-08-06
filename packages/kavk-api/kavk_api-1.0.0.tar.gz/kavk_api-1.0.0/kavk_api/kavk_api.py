from .exceptions import VkError
from .api.methods import *
from .upload import Upload
from aiohttp import ClientSession
from typing import Callable,Optional
import asyncio_atexit

class Captcha:
    def __init__(self, captcha:dict) -> None:
        self.raw:dict = captcha
        self.img:str = captcha['captcha_img']
        self.sid:str = captcha['captcha_sid']


class Vk:
    '''A class for working with the VKontakte API

    `token`:`str`
        VK token
    `captcha_handler`:`Optional[Callable[[Captcha], str]]` = None
        Captcha handler function
    `client`:`ClientSession(conn_timeout=60)`
        Initialized aiohttp.ClientSession
    `version`:`str` = "5.131"
        API VK version
    `_url`:`str` = "https://api.vk.com/method/"
        URL for API requests
        '''
    def __init__(self, token:str, captcha_handler:Optional[Callable[[Captcha], str]]=None, 
                version="5.131", _url:str="https://api.vk.com/method/") -> None:
        self.token = token
        self.captcha_handler = captcha_handler
        self.client = ClientSession(conn_timeout=60)
        self._url = _url
        self._version = version
        self._params = {'access_token': self.token,
                        'v' : self._version}
        self.upload = Upload(self)
        # Дальше скучно
        self.account = Account(self)
        self.ads = Ads(self)
        self.adsweb = Adsweb(self)
        self.apps = Apps(self)
        self.auth = Auth(self)
        self.board = Board(self)
        self.database = Database(self)
        self.docs = Docs(self)
        self.donut = Donut(self)
        self.fave = Fave(self)
        self.friends = Friends(self)
        self.gifts = Gifts(self)
        self.groups = Groups(self)
        self.likes = Likes(self)
        self.market = Market(self)
        self.messages = Messages(self)
        self.newsfeed = Newsfeed(self)
        self.notes = Notes(self)
        self.notifications = Notifications(self)
        self.orders = Orders(self)
        self.pages = Pages(self)
        self.photos = Photos(self)
        self.podcasts = Podcasts(self)
        self.polls = Polls(self)
        self.search = Search(self)
        self.secure = Secure(self)
        self.stats = Stats(self)
        self.status = Status(self)
        self.storage = Storage(self)
        self.store = Store(self)
        self.stories = Stories(self)
        self.streaming = Streaming(self)
        self.users = Users(self)
        self.utils = Utils(self)
        self.video = Video(self)
        self.wall = Wall(self)
        self.widgets = Widgets(self)
        # Скука закончилась!
        asyncio_atexit.register(self._on_exit)

    async def call_method(self, method:str, **params) -> dict:
        params.update(self._params)
        params = {k:v for k, v in params.items() if v is not None} #  Remove anything that has a value of None
        async with self.client.get(self._url+method, params=params) as r:
            r = await r.json()
            return await self._error_handler(r, method, **params)

    async def _error_handler(self, response:dict, method:str, **params) -> dict:
        code = self._check_for_error(response)
        if code == 0:
            return response['response']
        elif code == 14 and self.captcha_handler != None:
            captcha = Captcha(response['error'])
            captcha_key = self.captcha_handler(captcha)
            params.update({'captcha_key': captcha_key,
                           'captcha_sid': captcha.sid})
            return await self.call_method(method, **params)
        else: raise VkError(response['error'])


    def _check_for_error(self, response:dict) -> int:
        return response.get('error', {}).get('error_code', 0)

    async def _on_exit(self) -> None:
        await self.client.close()


__all__ = ("Vk", "Captcha")
