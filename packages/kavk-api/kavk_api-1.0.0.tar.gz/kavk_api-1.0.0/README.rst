.. image :: https://i.imgur.com/yqfZiRG.png
   :align: center
   :alt: KAVK_API logo


.. image :: https://img.shields.io/pypi/v/kavk_api?style=for-the-badge
   :alt: PyPi version
   :target: https://pypi.python.org/pypi/kavk_api

.. image :: https://img.shields.io/pypi/l/kavk_api?style=for-the-badge
   :alt: MIT License
   :target: https://pypi.python.org/pypi/kavk_api

.. image :: https://img.shields.io/badge/VK-Contact-blue?style=for-the-badge
   :alt: https://vk.com/klm_ahmed
   :target: https://vk.com/klm_ahmed

=========

Установка
---------
``pip install kavk_api``

TODO:
-------
* замена asyncio.run()


Пример:
-------
.. code-block:: python

        import asyncio
        from kavk_api import Vk
        from kavk_api.longpoll.bot import BotLongPoll

        async def main():
            vk = Vk('token')
            longpoll = LongPoll(vk)
            await vk.wall.post(message="Привет kavk_api!")
            async for event in longpoll.listen():
                print(event.type, event.object)
      
  
        asyncio.run(main())
