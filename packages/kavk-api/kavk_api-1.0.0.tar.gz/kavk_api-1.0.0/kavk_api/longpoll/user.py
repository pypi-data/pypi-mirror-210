from ..events import user_events as UserEvents
from ..events import enums as UserEnums
from ..kavk_api import Vk
from ..events.enums import DEFAULT_MODE

class UserLongPoll:
    def __init__(self, vk:Vk, _wait:int=25, _mode:int=DEFAULT_MODE, _v:int=3) -> None:
        self._vk = vk
        self._wait = _wait
        self._mode = _mode
        self._v = _v
        self._params = {}
        self._server = ''
        self._updates = []

    async def listen(self):
        while 1:
            async for event in UserLongPoll(self._vk, self._wait, self._mode, self._v):
                yield event 

    async def _get_event_raw(self, url:str, params:dict) -> dict:
        r = await self._vk.client.get(url=url, params=params)
        r = await r.json()
        return r

    async def _update_params(self) -> None:
        r = await self._vk.messages.getLongPollServer(lp_version=self._v)
        self._params = {'key': r.key, 'ts': r.ts,
                        'wait': self._wait, 'mode': self._mode,
                       'version': self._v, 'act': 'a_check'}
        self._server = 'https://'+r.server

    async def _get_event(self) -> list:
        r = await self._get_event_raw(url=self._server, params=self._params)
        try:
            updates:list = r['updates']
            self._params.update({'ts': r['ts']})
            return updates
        except IndexError:
            error = r['failed']
            if error == 1:
                self._params.update({'ts': r['ts']})
            elif error in (2,3):
                self._params.clear()
            elif error == 4:
                self._params.update({'v': r['min_version']})
            updates = []

            return updates
        except Exception as e:
            raise e


    # Что происходит дальше?
    # __aiter__ возвращает коду `async for e in UserLongPoll.listem()`
    # функцию __anext__.
    # Она же в свою очередь просто получает наш новый ивент

    def __aiter__(self): return self

    async def __anext__(self):
        if self._params == {}: 
            await self._update_params()

        if self._updates != []:
            u = self._updates.pop(0)
            return UserEvents._get_event(u)
        
        updates = []
        while updates == []:
            updates = await self._get_event()
            if len(updates) > 0:
                if updates[0][0] > 600: # Игнорим ивенты реакций
                    updates.clear()
        
        if len(updates) > 0:
            self._updates = updates[1:]
            update = updates[0]
        else:
            update = updates
        return UserEvents._get_event(update)


__all__ = ("UserEvents", "UserLongPoll", "UserEnums")
