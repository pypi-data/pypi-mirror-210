from ..kavk_api import Vk
from ..events import bot_events as BotEvent


class BotLongPoll:
    '''
        Класс для работы с BotLongPoll

        ...
        
        vk:Vk
            Объект kavk_api.Vk
        wait:int = 25
            Время ожидания
    '''
    def __init__(self, vk:Vk, wait:int=25) -> None:
        self._vk:Vk = vk
        self._wait:int = wait
        self._server:str = ''
        self._params:dict = {}
        self._updates:list = []

    async def listen(self):
        '''Генератор ивентов BotLongPoll'''
        while 1:
            async for event in BotLongPoll(self._vk, self._wait):
                yield event

    async def _update_params(self) -> None:
        '''Обновление self._params и self._server'''
        group_id = await self._vk.groups.getById()
        self.group_id = group_id[0].id
        r = await self._vk.groups.getLongPollServer(group_id=self.group_id)
        self._params.update({'key': r.key, 'ts': r.ts, 'wait': self._wait, 'act':'a_check'})
        self._server = r.server

    
    async def _get_event(self) -> list:
        '''Получение списка сырых ивентов'''
        if self._params == {}:
            await self._update_params()
        r = await self._vk.client.get(url=self._server, params=self._params)
        r = await r.json()
        updates:list|None = r.get('updates', None)
        if updates == None:
            try:
                error = r['failed']
                if error == 1:
                    self._params.update({'ts': r['ts']})
                elif error == 2 or error == 3:
                    self._params.clear()
                updates = []
            except Exception as e:
                raise e
        else: self._params.update({'ts': r['ts']})

        return updates

    # Что происходит дальше?
    # __aiter__ возвращает коду `async for e in LongPoll.listen()`
    # функцию __anext__.
    # Она же в свою очередь просто получает наш новый ивент и обрабатывает его

    def __aiter__(self): return self

    async def __anext__(self):
        if self._updates != []:
            u:dict = self._updates.pop(0)
            event = BotEvent._get_event(u.get('type',''))
            return event(**u, raw=u)
            
        updates = []
        while updates == []:
            '''
            Если событий за время self._wait не произойдёт, мы получим в ответ пустой список.
            Т.к. делать ивент из такого ответа хз как, мы просто ждем когда прийдет нормальный
            '''
            updates = await self._get_event() 
        
        if len(updates) > 0:
            self._updates = updates[1:]
            update:dict = updates[0]
        else: update:dict = updates[0]
        event_type = str(update.get('type', ''))
        event = BotEvent._get_event(event_type)
        return event(**update, raw=update)

__all__ = ("BotLongPoll", 'BotEvent')
