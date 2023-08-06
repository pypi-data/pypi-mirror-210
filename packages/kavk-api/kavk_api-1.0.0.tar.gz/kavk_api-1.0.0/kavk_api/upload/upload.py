from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from io import BytesIO
from .responses import VideoSaveResponse
try:
    import orjson as json
except:
    import json as json
if TYPE_CHECKING:
    from ..kavk_api import Vk

class Upload:
    '''
    A class for uploading files for VK
    ...

    `vk`:`Vk` 
    `group_id`:`int` - Optional parameter
    '''
    def __init__(self, vk:Vk, group_id:int|None = None) -> None:
        self._vk = vk
        self._client = vk.client
        self.group_id = group_id

    def _get_data(self, files:list[str]) -> dict[str, BytesIO]:
        data:dict[str, BytesIO] = {}
        for i, f in enumerate(files):
            bytes = BytesIO(open(f, 'rb').read())
            bytes.name = f
            data.update({f'file{i+1}': bytes})
        if len(data) == 1:
            data.update({'file': data['file1']})
            data.pop('file1')
        return data

    def _get_list(self, any) -> list:
        if not isinstance(any, list):
            any = [any]
        return any

    def _check_list(self, lst:list, max:int=10, min:int=1) -> None:
        if len(lst) > max:
            raise ValueError('You cannot upload more than {} files at a time!'.format(max))
        elif len(lst) < min:
            raise ValueError('You cannot upload less than {} files at a time!'.format(min))

    async def _upload_files(self, url:str, files:dict[str, BytesIO]) -> dict:
        # the retards at VK send the response to the request below in text, not json, so do what's below
        return json.loads(
                await (await self._client.post(url=url, data=files)).text()
                )

    async def photo_in_message(self, photo_path:list[str]|str) -> str:
        '''Uploading photos to message
        Returns a string matching the `attachments` parameter of the `Vk.messages.send` method'''
        photo_path = self._get_list(photo_path)
        self._check_list(photo_path)
        files = self._get_data(photo_path)
        url = (await self._vk.photos.getMessagesUploadServer()).upload_url
        response = await self._upload_files(url, files)
        # Saving photos
        resp = await self._vk.photos.saveMessagesPhoto(photo=response['photo'], server=response['server'],
                                                       hash=response['hash']
                                                       )
        return_str = ''
        for i in resp:
            return_str = return_str + (',photo{}_{}'.format(i.owner_id, i.id))
        return return_str

    async def photo_in_album(self, photo_path:list[str]|str, album_id:int, latitude:Optional[int] = None,
                             longitude:Optional[int] = None, caption:Optional[str] = None):
        '''Uploading photos to an album'''
        photo_path = self._get_list(photo_path)
        self._check_list(photo_path, 5)
        files = self._get_data(photo_path)
        url = (await self._vk.photos.getUploadServer(album_id=album_id, group_id=self.group_id)).upload_url
        response = await self._upload_files(url, files)
        # Saving photos
        return await self._vk.photos.save(album_id=album_id,group_id=self.group_id, server=response['server'], 
                                          photos_list=response['photos_list'], hash=response['hash'],
                                          longitude=longitude, latitude=latitude, caption=caption
                                          )

    async def main_photo(self, photo_path:str):
        '''Uploading main photo of the user or public'''
        files = self._get_data([photo_path])
        if self.group_id != None: owner_id = self.group_id
        else: owner_id = (await self._vk.users.get())[0].id
        url = (await self._vk.photos.getOwnerPhotoUploadServer(owner_id=owner_id)).upload_url
        response = await self._upload_files(url, files)
        # Saving photo
        return await self._vk.photos.saveOwnerPhoto(server=response['server'], hash=response['hash'],
                                                    photo=response['photo'])

    async def wall_photo(self, photo_path:list[str]|str, longitude:Optional[int]=None,
                         latitude:Optional[int]=None, caption:Optional[str]=None) -> str:
        '''Uploading a photo to the wall
        Returns a string matching the `attachments` parameter of the `Vk.wall.post` method'''
        photo_path = self._get_list(photo_path)
        self._check_list(photo_path)
        files = self._get_data(photo_path)
        url = (await self._vk.photos.getWallUploadServer(self.group_id)).upload_url
        response = await self._upload_files(url, files)
        resp = await self._vk.photos.saveWallPhoto(photo=response['photo'], server=response['server'], 
                                                   hash=response['hash'], 
                                                   longitude=longitude, latitude=latitude, caption=caption
                                                   )
        return_str = ''
        for i in resp:
            return_str = return_str + (',photo{}_{}'.format(i.owner_id, i.id))
        return return_str
        
    async def chat_main_photo(self, photo_path:str, chat_id:int, crop_x:Optional[int]=None,
                              crop_y:Optional[int]=None, crop_width:Optional[int]=None):
        '''Uploading a main photo for the chat'''
        files = self._get_data([photo_path])
        url = (await self._vk.photos.getChatUploadServer(chat_id=chat_id, crop_x=crop_x,
                                                         crop_y=crop_y, crop_width=crop_width)
               ).upload_url
        response = await self._upload_files(url, files)
        return await self._vk.messages.setChatPhoto(response['response'])

    async def video(self, video_path:Optional[str]=None, link:Optional[str]=None, **kwargs):
        '''Uploading a video'''
        if link != None:
            return await self._vk.video.save(link=link, group_id=self.group_id, **kwargs)
        elif video_path == None:
            raise ValueError('At least one of the parameters must be specified!')
        files = self._get_data([video_path])
        url = (await self._vk.video.save(**kwargs)).upload_url
        return VideoSaveResponse.parse_obj(await self._upload_files(url, files))
    
    async def document(self, doc_path:str, to_wall:bool=False, to_message:bool=False, audio_message:bool=False, 
                       title:Optional[str]=None, tags:Optional[str]=None):
        '''Uploading a document'''
        files = self._get_data([doc_path])
        if to_wall: resp = await self._vk.docs.getWallUploadServer(self.group_id)
        elif to_message: resp = await self._vk.docs.getMessagesUploadServer(type='doc')
        elif audio_message: resp = await self._vk.docs.getMessagesUploadServer(type='audio_message')
        else: resp = await self._vk.docs.getUploadServer(self.group_id)
        url = resp.upload_url
        response = await self._upload_files(url, files)
        return await self._vk.docs.save(file=response['file'], title=title, tags=tags)

    async def photo_cover(self, photo_path:str, crop_x:Optional[int]=None, crop_y:Optional[int]=None,
                          crop_x2:Optional[int]=None, crop_y2:Optional[int]=None):
        '''Uploading a cover'''
        files = self._get_data([photo_path])
        url = (await self._vk.photos.getOwnerCoverPhotoUploadServer(self.group_id, crop_x, crop_y, 
                                                                    crop_x2, crop_y2)
               ).upload_url
        response = await self._upload_files(url, files)
        return await self._vk.photos.saveOwnerCoverPhoto(response['hash'], response['photo'])

    async def audio_message(self, audio_path:str):
        '''Uploading a audio message'''
        response = await self.document(audio_path, audio_message=True)
        return 'audio{}_{}'.format(response.audio_message.owner_id, response.audio_message.id)



